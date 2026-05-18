from fastapi import APIRouter, Depends, HTTPException, Request
from src.helpers.limiter import limiter
from sqlalchemy.orm import Session
from uuid import UUID
from src.models.verifications_models import PresignRequest, PresignResponse, ConfirmRequest, PhotoViewResponse, QuizQuestionResponse, QuizSubmitRequest, VerificationTypeResponse, CreateVerificationResponse
from src.models import verifications_schemas, goal_schemas, auth_schemas
from src.helpers.s3 import (
    build_s3_key,
    presign_put,
    presign_get,
    object_exists,
    build_s3_uri,
    parse_s3_uri,
)
from src.helpers.db import get_db
from src.helpers.auth_utils import validate_access_token
from src.tasks.evaluations import evaluate_photo_verification
from src.helpers.verification_utils import get_quizzes, get_user, get_verification_and_goal, is_admin_or_owner, evaluate_quiz_submission

router = APIRouter(prefix="/api/v1/verification", tags=["Goals"])

@router.get("/verification-type/{goal_id}")
@limiter.limit("20/minute")
def get_verification_type(
    request: Request,
    goal_id: UUID,
    response_model=VerificationTypeResponse,
    user_id: UUID = Depends(validate_access_token),
    db: Session = Depends(get_db)
):
    goal = db.query(goal_schemas.Goal).filter(goal_schemas.Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    verify_type = goal.goal_type.verification_type
    
    if (verify_type == "quiz"):
        rows = (db.query(verifications_schemas.QuizQuestions)
                          .filter(verifications_schemas.QuizQuestions.goal_id == goal_id))
        questions = [{"quiz_id": q.id, "question": q.question} for q in rows]
    return VerificationTypeResponse(
        verification_type=verify_type,
        questions=questions,
    )

@router.post("/create/{goal_id}", response_model=CreateVerificationResponse)
@limiter.limit("100/hour")
def create_verification(
    request: Request,
    goal_id: UUID,
    user_id: UUID = Depends(validate_access_token),
    db: Session = Depends(get_db)
):
    goal = db.query(goal_schemas.Goal).filter(goal_schemas.Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    user = get_user(db, user_id)
    if not is_admin_or_owner(user, goal.user_id):
        raise HTTPException(status_code=403, detail="Not authorized to verify this goal")
    if goal.goal_type.verification_type != "photo":
        raise HTTPException(status_code=400, detail="Verification type must be photo")
    existing = (
        db.query(verifications_schemas.Verification)
        .filter(verifications_schemas.Verification.goal_id == goal_id)
        .filter(verifications_schemas.Verification.verification_type == "photo")
        .filter(verifications_schemas.Verification.result == "pending")
        .first()
    )
    if existing:
        return CreateVerificationResponse(verification_id=str(existing.id))
    record = verifications_schemas.Verification(
        goal_id=goal_id,
        verification_type="photo",
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return CreateVerificationResponse(verification_id=str(record.id))

@router.get("/getquiz/{goal_id}")
@limiter.limit("20/minute")
def get_quiz(
    request: Request,
    goal_id: UUID,
    response_model=QuizQuestionResponse,
    user_id: UUID = Depends(validate_access_token),
    db: Session = Depends(get_db)
):
    return get_quizzes(db, goal_id)
    

@router.post("/quiz/submit")
@limiter.limit("20/hour")
def quiz_submit(
    request: Request,
    payload: QuizSubmitRequest,
    user_id: UUID = Depends(validate_access_token),
    db: Session = Depends(get_db)
):
    result = evaluate_quiz_submission(db, payload.goal_id, payload.user_submission)
    return {"result": result}

@router.post("/photos/presign", response_model=PresignResponse)
@limiter.limit("20/hour")
def presign(
    request: Request,
    req: PresignRequest,
    user_id: UUID = Depends(validate_access_token),
    db: Session = Depends(get_db)
):
    ext = req.file_ext.lower().strip()
    if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        raise HTTPException(400, "Unsupported file type")
    if not req.content_type.startswith("image/"):
        raise HTTPException(400, "Unsupported content type")

    user = get_user(db, user_id)
    verification, goal = get_verification_and_goal(db, req.verification_id)
    if verification.verification_type != "photo":
        raise HTTPException(status_code=400, detail="Verification type must be photo")
    if not is_admin_or_owner(user, goal.user_id):
        raise HTTPException(status_code=403, detail="Not authorized to upload this photo")

    key = build_s3_key(user_id=str(goal.user_id), verification_id=req.verification_id, ext=ext)
    upload_url = presign_put(key=key, content_type=req.content_type)
    return PresignResponse(upload_url=upload_url, s3_key=key)


@router.post("/photos/confirm")
@limiter.limit("20/hour")
def confirm(
    request: Request,
    req: ConfirmRequest,
    user_id: UUID = Depends(validate_access_token),
    db: Session = Depends(get_db),
):
    user = get_user(db, user_id)
    verification, goal = get_verification_and_goal(db, req.verification_id)
    if verification.verification_type != "photo":
        raise HTTPException(status_code=400, detail="Verification type must be photo")
    if not is_admin_or_owner(user, goal.user_id):
        raise HTTPException(status_code=403, detail="Not authorized to confirm this photo")

    expected_prefix = f"verifications/{goal.user_id}/{req.verification_id}/"
    if not req.s3_key.startswith(expected_prefix):
        raise HTTPException(status_code=400, detail="Unexpected S3 key")
    if not object_exists(req.s3_key):
        raise HTTPException(status_code=400, detail="S3 object not found")

    existing = (
        db.query(verifications_schemas.VerificationPhoto)
        .filter(verifications_schemas.VerificationPhoto.verification_id == req.verification_id)
        .first()
    )
    image_url = build_s3_uri(req.s3_key)
    meta = dict(req.meta or {})

    if existing:
        existing.image_url = image_url
        existing.s3_key = req.s3_key
        existing.meta = meta
    else:
        record = verifications_schemas.VerificationPhoto(
            verification_id=req.verification_id,
            image_url=image_url,
            s3_key=req.s3_key,
            meta=meta,
        )
        db.add(record)
    goal.status = "validating"
    db.commit()
    evaluate_photo_verification.delay(req.verification_id)
    return {"ok": True}


@router.get("/verification-photos/{verification_id}", response_model=PhotoViewResponse)
@limiter.limit("20/minute")
def get_photo(
    request: Request,
    verification_id: str,
    user_id: UUID = Depends(validate_access_token),
    db: Session = Depends(get_db),
):
    user = get_user(db, user_id)
    verification, goal = get_verification_and_goal(db, verification_id)
    if not is_admin_or_owner(user, goal.user_id):
        raise HTTPException(status_code=403, detail="Not authorized to view this photo")

    photo = (
        db.query(verifications_schemas.VerificationPhoto)
        .filter(verifications_schemas.VerificationPhoto.verification_id == verification_id)
        .first()
    )
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    s3_key = photo.s3_key or parse_s3_uri(photo.image_url)
    if not s3_key:
        raise HTTPException(status_code=500, detail="Photo key missing")

    view_url = presign_get(s3_key)
    return PhotoViewResponse(verification_id=verification_id, view_url=view_url)
