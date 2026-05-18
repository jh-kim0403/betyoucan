from datetime import datetime, timezone

from src.celery_app import celery_app
from src.helpers.db import SessionLocal
from src.helpers.maintenance_cost_utils import (
    ingest_weekly_maintenance_costs,
    calculation_window_utc,
)


@celery_app.task(bind=True, max_retries=0, default_retry_delay=60)
def ingest_maintenance_costs_for_window(
    self, week_start_iso: str | None = None, week_end_iso: str | None = None
):
    db = SessionLocal()
    try:
        if week_start_iso is None and week_end_iso is None:
            week_start, week_end = calculation_window_utc()
            source = "automated"
        elif week_start_iso is not None and week_end_iso is not None:
            week_start = datetime.fromisoformat(week_start_iso)
            week_end = datetime.fromisoformat(week_end_iso)
            if week_start.tzinfo is None:
                week_start = week_start.replace(tzinfo=timezone.utc)
            if week_end.tzinfo is None:
                week_end = week_end.replace(tzinfo=timezone.utc)
            source = "manual-trigger"
        else:
            raise ValueError("Both week_start_iso and week_end_iso must be provided")

        result = ingest_weekly_maintenance_costs(
            db=db,
            week_start=week_start,
            week_end=week_end,
            source=source,
        )
        return {
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "aws_cost_cents": result.aws_cost_cents,
            "openai_cost_cents": result.openai_cost_cents,
            "fee_amount_cents": result.fee_amount_cents,
        }
    except Exception as exc:
        raise self.retry(exc=exc)
    finally:
        db.close()
