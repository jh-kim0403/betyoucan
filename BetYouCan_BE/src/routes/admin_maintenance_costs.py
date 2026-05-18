from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from src.helpers.auth_utils import validate_access_token
from src.helpers.db import get_db
from src.models.auth_schemas import User
from src.models.maintenance_cost_models import (
    MaintenanceCostIngestRequest,
    MaintenanceCostResponse,
    MaintenanceCostUpsertRequest,
)
from src.models.maintenance_cost_schemas import WeeklyMaintenanceCost
from src.tasks.maintenance_cost_tasks import ingest_maintenance_costs_for_window

router = APIRouter(prefix="/api/v1/admin/maintenance-costs", tags=["Admin"])


def _require_admin(db: Session, user_id: UUID) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    return user


@router.post("/ingest")
def queue_ingest(
    payload: MaintenanceCostIngestRequest | None = None,
    user_id: UUID = Depends(validate_access_token),
    db: Session = Depends(get_db),
):
    _require_admin(db, user_id)
    if payload is None:
        task = ingest_maintenance_costs_for_window.delay()
    else:
        task = ingest_maintenance_costs_for_window.delay(
            payload.week_start.isoformat(), payload.week_end.isoformat()
        )
    return {"task_id": task.id}


@router.post("/upsert", response_model=MaintenanceCostResponse)
def upsert_costs(
    payload: MaintenanceCostUpsertRequest,
    user_id: UUID = Depends(validate_access_token),
    db: Session = Depends(get_db),
):
    _require_admin(db, user_id)
    fee_amount_cents = payload.aws_cost_cents + payload.openai_cost_cents
    stmt = insert(WeeklyMaintenanceCost).values(
        week_start=payload.week_start,
        week_end=payload.week_end,
        aws_cost_cents=payload.aws_cost_cents,
        openai_cost_cents=payload.openai_cost_cents,
        fee_amount_cents=fee_amount_cents,
        source="admin-manual",
        notes=payload.notes,
        meta={"updated_by": str(user_id)},
    )
    stmt = stmt.on_conflict_do_update(
        constraint="uq_weekly_maintenance_cost_window",
        set_={
            "aws_cost_cents": payload.aws_cost_cents,
            "openai_cost_cents": payload.openai_cost_cents,
            "fee_amount_cents": fee_amount_cents,
            "source": "admin-manual",
            "notes": payload.notes,
            "meta": {"updated_by": str(user_id)},
            "updated_at": datetime.now(timezone.utc),
        },
    )
    db.execute(stmt)
    db.commit()

    row = (
        db.query(WeeklyMaintenanceCost)
        .filter(WeeklyMaintenanceCost.week_start == payload.week_start)
        .filter(WeeklyMaintenanceCost.week_end == payload.week_end)
        .first()
    )
    return row


@router.get("/latest", response_model=MaintenanceCostResponse)
def get_latest_cost(
    user_id: UUID = Depends(validate_access_token),
    db: Session = Depends(get_db),
):
    _require_admin(db, user_id)
    row = (
        db.query(WeeklyMaintenanceCost)
        .order_by(WeeklyMaintenanceCost.week_start.desc())
        .first()
    )
    if row is None:
        raise HTTPException(status_code=404, detail="No maintenance cost records found")
    return row
