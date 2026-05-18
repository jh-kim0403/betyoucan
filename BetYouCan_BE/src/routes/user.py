import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status, Response
from src.helpers.limiter import limiter
from sqlalchemy.orm import Session
from uuid import UUID
from src.helpers.db import get_db
from src.helpers.auth_utils import validate_access_token, hash_refresh_token
from src.models.users_models import UsersResponseModel
from src.models.auth_schemas import User, RefreshToken
from src.models.auth_models import LogOutRequest


router = APIRouter(prefix="/api/v1/user", tags=["User"])

@router.get(path="/profile", response_model=UsersResponseModel)
@limiter.limit("20/minute")
def get_profile(request: Request, user_id: UUID = Depends(validate_access_token), db: Session = Depends(get_db)):
    rs = db.query(User).filter(User.id == user_id).first()
    if rs is None:
        raise HTTPException(status_code=404, detail="User not found")

    logging.info(rs.email)
    return rs

@router.post("/logout")
@limiter.limit("5/minute")
def logout(request: Request, payload: LogOutRequest, response: Response, db: Session = Depends(get_db)):
    try:
        rs = (db.query(RefreshToken)
            .filter(RefreshToken.token == hash_refresh_token(payload.refresh_token))
            .first())
        if rs:
            db.delete(rs)
            db.commit()
            return {"message": "Logged out successfully"}
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed",
        )