from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

import requests
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from src.config import settings
from src.models.maintenance_cost_schemas import WeeklyMaintenanceCost


def _to_cents(amount: Decimal | float | int | str) -> int:
    cents = (Decimal(str(amount)) * Decimal("100")).quantize(
        Decimal("1"), rounding=ROUND_HALF_UP
    )
    return int(cents)


def calculation_window_utc(now: datetime | None = None) -> tuple[datetime, datetime]:
    current = now or datetime.now(timezone.utc)
    week_start_this = (current - timedelta(days=current.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    # Use the week window from 3 weeks prior to allow contest periods before payout.
    week_start_prior = week_start_this - timedelta(days=8)
    week_end_prior = week_start_this - timedelta(days=1)
    return week_start_prior, week_end_prior


@dataclass
class WeeklyCostResult:
    aws_cost_cents: int
    openai_cost_cents: int
    fee_amount_cents: int
    meta: dict[str, Any]


def fetch_aws_cost_cents(week_start: datetime, week_end: datetime) -> tuple[int, dict[str, Any]]:
    import boto3

    client = boto3.client(
        "ce",
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key,
        aws_secret_access_key=settings.aws_secret_key,
    )
    response = client.get_cost_and_usage(
        TimePeriod={
            "Start": week_start.date().isoformat(),
            "End": week_end.date().isoformat(),
        },
        Granularity="MONTHLY",
        Metrics=["UnblendedCost"],
    )
    amount = (
        response.get("ResultsByTime", [{}])[0]
        .get("Total", {})
        .get("UnblendedCost", {})
        .get("Amount", "0")
    )
    return _to_cents(amount), {"provider_response": response}


def _extract_openai_cost_amount(payload: dict[str, Any]) -> Decimal:
    if "total_cost" in payload:
        return Decimal(str(payload["total_cost"]))
    if "amount" in payload and isinstance(payload["amount"], dict):
        if "value" in payload["amount"]:
            return Decimal(str(payload["amount"]["value"]))

    data = payload.get("data") or payload.get("results") or []
    total = Decimal("0")
    for item in data:
        if not isinstance(item, dict):
            continue
        if "amount" in item:
            if isinstance(item["amount"], dict) and "value" in item["amount"]:
                total += Decimal(str(item["amount"]["value"]))
            elif isinstance(item["amount"], (int, float, str)):
                total += Decimal(str(item["amount"]))
            continue
        if "total_cost" in item:
            total += Decimal(str(item["total_cost"]))
    return total


def fetch_openai_cost_cents(
    week_start: datetime, week_end: datetime
) -> tuple[int, dict[str, Any]]:
    api_key = settings.openai_admin_api_key or settings.openai_api_key
    if not api_key:
        raise ValueError("OpenAI API key is missing for maintenance cost ingestion")

    headers = {"Authorization": f"Bearer {api_key}"}
    if settings.openai_org_id:
        headers["OpenAI-Organization"] = settings.openai_org_id

    response = requests.get(
        settings.openai_costs_api_url,
        headers=headers,
        params={
            "start_time": int(week_start.timestamp()),
            "end_time": int(week_end.timestamp()),
            "interval": "1d",
        },
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    amount_usd = _extract_openai_cost_amount(payload)
    return _to_cents(amount_usd), {"provider_response": payload}


def ingest_weekly_maintenance_costs(
    db: Session,
    week_start: datetime,
    week_end: datetime,
    source: str = "automated",
    notes: str | None = None,
) -> WeeklyCostResult:
    aws_meta: dict[str, Any] = {}
    openai_meta: dict[str, Any] = {}
    aws_cost_cents = 0
    openai_cost_cents = 0

    try:
        aws_cost_cents, aws_meta = fetch_aws_cost_cents(week_start=week_start, week_end=week_end)
    except Exception as exc:
        aws_meta = {"error": str(exc)}

    try:
        openai_cost_cents, openai_meta = fetch_openai_cost_cents(
            week_start=week_start, week_end=week_end
        )
    except Exception as exc:
        openai_meta = {"error": str(exc)}

    fee_amount_cents = aws_cost_cents + openai_cost_cents
    meta = {
        "aws": aws_meta,
        "openai": openai_meta,
    }

    stmt = insert(WeeklyMaintenanceCost).values(
        week_start=week_start,
        week_end=week_end,
        aws_cost_cents=aws_cost_cents,
        openai_cost_cents=openai_cost_cents,
        fee_amount_cents=fee_amount_cents,
        source=source,
        notes=notes,
        meta=meta,
    )
    stmt = stmt.on_conflict_do_update(
        constraint="uq_weekly_maintenance_cost_window",
        set_={
            "aws_cost_cents": aws_cost_cents,
            "openai_cost_cents": openai_cost_cents,
            "fee_amount_cents": fee_amount_cents,
            "source": source,
            "notes": notes,
            "meta": meta,
            "updated_at": datetime.now(timezone.utc),
        },
    )
    db.execute(stmt)
    db.commit()

    return WeeklyCostResult(
        aws_cost_cents=aws_cost_cents,
        openai_cost_cents=openai_cost_cents,
        fee_amount_cents=fee_amount_cents,
        meta=meta,
    )
