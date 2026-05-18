from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from src.celery_app import celery_app
from src.helpers.db import SessionLocal
from src.models import verifications_schemas


@celery_app.task(bind=True, max_retries=0, default_retry_delay=30)
def cleanup_abandoned_photo_verifications(self):
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

    db = SessionLocal()
    try:
        with db.begin():
            photo_ids_subquery = select(
                verifications_schemas.VerificationPhoto.verification_id
            )
            stale = (
                db.query(verifications_schemas.Verification)
                .filter(verifications_schemas.Verification.type == "photo")
                .filter(verifications_schemas.Verification.result == "pending")
                .filter(verifications_schemas.Verification.created_at < cutoff)
                .filter(~verifications_schemas.Verification.id.in_(photo_ids_subquery))
                .limit(200)
                .all()
            )
            deleted = 0
            for record in stale:
                db.delete(record)
                deleted += 1
        return {"deleted": deleted}
    finally:
        db.close()
