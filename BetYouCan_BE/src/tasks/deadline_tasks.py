import logging
from datetime import datetime, timezone
from sqlalchemy import or_
from src.celery_app import celery_app
from src.helpers.db import SessionLocal
from src.models.goal_schemas import Goal
from src.models.verifications_schemas import Verification

logger = logging.getLogger(__name__)


def _ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


@celery_app.task(bind=True, max_retries=0)
def finalize_goal_at_deadline(self, goal_id: str):
    logger.info("finalize_goal_at_deadline start goal_id=%s", goal_id)
    db = SessionLocal()
    try:
        with db.begin():
            goal = (
                db.query(Goal)
                .filter(Goal.id == goal_id)
                .with_for_update()
                .first()
            )
            if goal is None:
                logger.warning("finalize_goal_at_deadline goal_not_found goal_id=%s", goal_id)
                return {"status": "missing", "goal_id": goal_id}

            if goal.status == "resolved":
                logger.info("finalize_goal_at_deadline already_resolved goal_id=%s", goal_id)
                return {"status": "already_resolved", "goal_id": goal_id}

            now = datetime.now(timezone.utc)
            if _ensure_utc(goal.deadline) > now:
                logger.info("finalize_goal_at_deadline not_due_yet goal_id=%s deadline=%s", goal_id, goal.deadline)
                return {"status": "not_due_yet", "goal_id": goal_id}

            latest_verification = (
                db.query(Verification)
                .filter(Verification.goal_id == goal.id)
                .order_by(Verification.updated_at.desc())
                .first()
            )
            is_approved = bool(
                latest_verification is not None and latest_verification.result == "completed"
            )

            goal.verification_status = "completed" if is_approved else "failed"
            goal.status = "resolved"
            goal.completed_at = now

            logger.info("finalize_goal_at_deadline resolved goal_id=%s verification_status=%s", goal_id, goal.verification_status)

        return {"status": "ok", "goal_id": goal_id}
    except Exception:
        logger.exception("finalize_goal_at_deadline failed goal_id=%s", goal_id)
        db.rollback()
        raise
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def sweep_overdue_goals(self):
    now = datetime.now(timezone.utc)
    db = SessionLocal()
    try:
        overdue_goal_ids = (
            db.query(Goal.id)
            .filter(Goal.deadline <= now)
            .filter(Goal.completed_at.is_(None))
            .filter(
                or_(
                    Goal.status == "active",
                    Goal.status == "validating",
                    Goal.status.is_(None),
                )
            )
            .limit(500)
            .all()
        )

        for (goal_id,) in overdue_goal_ids:
            finalize_goal_at_deadline.delay(str(goal_id))

        return {"queued": len(overdue_goal_ids)}
    finally:
        db.close()
