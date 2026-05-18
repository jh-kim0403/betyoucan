from uuid import UUID
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.models import goal_schemas
from datetime import datetime, timezone, timedelta

def get_goal_type_or_404(goal_type_id: UUID, db: Session) -> goal_schemas.GoalType:
    goal_type = db.query(goal_schemas.GoalType).filter(goal_schemas.GoalType.id == goal_type_id).first()
    if not goal_type:
        raise HTTPException(status_code=400, detail="Invalid goal type")
    return goal_type

def has_reached_free_tier_limit(user_id: UUID, db: Session) -> bool:
    one_week_ago = datetime.now(timezone.utc) - timedelta(weeks=1)
    recent_goal = (
        db.query(goal_schemas.Goal)
        .filter(goal_schemas.Goal.user_id == user_id)
        .filter(goal_schemas.Goal.created_at >= one_week_ago)
        .first()
    )
    return recent_goal is not None

def current_goals_and_verifications_for_user(user_id: UUID, db: Session):
    query = """
SELECT
  g.*,
  v_latest.id          AS verification_id,
  gt.name              AS goal_type_name,
  gt.verification_type AS verification_type,
  v_latest.result      AS verification_result,
  v_latest.updated_at  AS verification_updated_at
FROM goals g
LEFT JOIN goal_types gt
  ON gt.id = g.goal_type_id
LEFT JOIN LATERAL (
  SELECT v.*
  FROM verifications v
  WHERE v.goal_id = g.id
  ORDER BY v.updated_at DESC
  LIMIT 1
) v_latest ON TRUE
WHERE g.deadline >= now()
AND g.user_id = :user_id;
            """

    return db.execute(text(query), {"user_id": str(user_id)}).fetchall()
