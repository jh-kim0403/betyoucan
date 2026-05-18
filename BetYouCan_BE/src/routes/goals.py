from fastapi import APIRouter, Depends, HTTPException, Request, status
from src.helpers.limiter import limiter
from sqlalchemy.orm import Session, joinedload
import logging
from typing import Optional
from datetime import datetime, timezone
from src.helpers.bounty_ledger_utils import apply_bounty_ledger_entry
from src.helpers.goals_utils import get_goal_type_or_404, has_reached_free_tier_limit
from ..helpers.auth_utils import validate_access_token
from uuid import UUID
from ..models import goal_models, goal_schemas
from ..models import auth_schemas 
from ..helpers.db import get_db
from src.tasks.quiz_tasks import generate_quiz_for_goal
from src.tasks.deadline_tasks import finalize_goal_at_deadline

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/goals", tags=["Goals"])


def _schedule_goal_tasks(goal: goal_schemas.Goal, goal_type: goal_schemas.GoalType):
    if goal_type.verification_type == "quiz":
        generate_quiz_for_goal.delay(str(goal.id))
    finalize_goal_at_deadline.apply_async(args=[str(goal.id)], eta=goal.deadline)


@router.post("/", response_model=goal_models.goalResponse)
@limiter.limit("30/hour")
def create_goal(
    request: Request,
    payload: goal_models.goalRequest,
    user_id: UUID = Depends(validate_access_token),
    db: Session = Depends(get_db),
):
    
    logger.info("create_goal request user_id=%s goal_type_id=%s", user_id, payload.goal_type_id)
    # IMPLEMENT FREE TIER LIMIT
    # user = db.query(auth_schemas.User).filter(auth_schemas.User.id == user_id).first()

    # if user.subscription_tier != "pro" and has_reached_free_tier_limit(user_id, db):
    #     logger.warning("free_tier_limit_reached user_id=%s", user_id)
    #     raise HTTPException(status_code=403, detail="Free tier allows only 1 goal per week")

    if payload.deadline <= datetime.now(timezone.utc):
        logger.warning("invalid_deadline user_id=%s deadline=%s", user_id, payload.deadline)
        raise HTTPException(status_code=400, detail="Deadline must be in the future")

    goal_type = get_goal_type_or_404(payload.goal_type_id, db)

    goal = goal_schemas.Goal(
        user_id=user_id,
        goal_type_id=payload.goal_type_id,
        title=payload.title,
        user_input=payload.user_input,
        bounty_amount=payload.bounty_amount,
        notification_tone=payload.notification_tone,
        deadline=payload.deadline,
        created_at=datetime.now(timezone.utc),
    )
    apply_bounty_ledger_entry(user_id, goal.id, "hold", payload.bounty_amount, db)
    db.add(goal)
    db.commit()
    db.refresh(goal)
    logger.info("goal_created goal_id=%s user_id=%s goal_type=%s deadline=%s", goal.id, user_id, goal_type.name, goal.deadline)

    _schedule_goal_tasks(goal, goal_type)
    logger.info("goal_tasks_scheduled goal_id=%s verification_type=%s", goal.id, goal_type.verification_type)

    return goal


@router.get("/goaltypes", response_model=list[goal_models.goalTypeResponse])
@limiter.limit("20/minute")
def get_goal_types(request: Request, user_id: UUID = Depends(validate_access_token), db: Session = Depends(get_db)):
    goal_types = db.query(goal_schemas.GoalType).all()
    if not goal_types:
        raise HTTPException(402, "Goal types not found")

    return [goal_models.goalTypeResponse.model_validate(r) for r in goal_types]


@router.get("/getcurrentgoals", response_model=list[goal_models.currentGoalResponse])
@limiter.limit("20/minute")
def get_current_goals(request: Request, user_id: UUID = Depends(validate_access_token), db: Session = Depends(get_db)):
    all_goals = (db.query(goal_schemas.Goal)
        .options(joinedload(goal_schemas.Goal.goal_type))
        .filter(
            goal_schemas.Goal.user_id == user_id,
            goal_schemas.Goal.deadline >= datetime.now(timezone.utc),
        )
        .all()
    )
    return [goal_models.currentGoalResponse.model_validate(r) for r in all_goals]
