from __future__ import annotations

from datetime import datetime, timezone
from celery import chain

from src.celery_app import celery_app
from src.helpers.bounty_ledger_utils import apply_bounty_ledger_entry
from src.helpers.db import SessionLocal
from src.helpers.maintenance_cost_utils import calculation_window_utc
from src.models.distribution_schemas import (
    WeeklyPoolDistribution,
    WeeklyPoolDistributionItem,
)
from src.models.goal_schemas import Goal
from src.models.maintenance_cost_schemas import WeeklyMaintenanceCost
from src.tasks.maintenance_cost_tasks import ingest_maintenance_costs_for_window


def _allocate_weighted_payouts(
    net_pool_cents: int, weighted_goals: list[tuple[str, int]]
) -> dict[str, int]:
    if net_pool_cents <= 0 or not weighted_goals:
        return {goal_id: 0 for goal_id, _ in weighted_goals}

    total_weight = sum(weight for _, weight in weighted_goals)
    if total_weight <= 0:
        return {goal_id: 0 for goal_id, _ in weighted_goals}

    base_allocations: dict[str, int] = {}
    remainders: list[tuple[str, int]] = []
    distributed = 0

    for goal_id, weight in weighted_goals:
        raw_numerator = net_pool_cents * weight
        base = raw_numerator // total_weight
        rem = raw_numerator % total_weight
        base_allocations[goal_id] = int(base)
        remainders.append((goal_id, int(rem)))
        distributed += int(base)

    left = net_pool_cents - distributed
    if left > 0:
        for goal_id, _ in sorted(remainders, key=lambda r: (-r[1], r[0]))[:left]:
            base_allocations[goal_id] += 1

    return base_allocations


@celery_app.task(bind=True, max_retries=0, default_retry_delay=60)
def distribute_weekly_pool(
    self,
    ingest_result: dict | None = None,
    week_start_iso: str | None = None,
    week_end_iso: str | None = None,
):
    if ingest_result and isinstance(ingest_result, dict):
        week_start_iso = week_start_iso or ingest_result.get("week_start")
        week_end_iso = week_end_iso or ingest_result.get("week_end")

    if week_start_iso is None or week_end_iso is None:
        week_start, week_end = calculation_window_utc()
    else:
        week_start = datetime.fromisoformat(week_start_iso)
        week_end = datetime.fromisoformat(week_end_iso)
        if week_start.tzinfo is None:
            week_start = week_start.replace(tzinfo=timezone.utc)
        if week_end.tzinfo is None:
            week_end = week_end.replace(tzinfo=timezone.utc)

    db = SessionLocal()
    try:
        with db.begin():
            existing = (
                db.query(WeeklyPoolDistribution)
                .filter(WeeklyPoolDistribution.week_start == week_start)
                .filter(WeeklyPoolDistribution.week_end == week_end)
                .first()
            )
            if existing is not None:
                return {
                    "status": "already_processed",
                    "week_start": week_start.isoformat(),
                    "week_end": week_end.isoformat(),
                    "distribution_id": str(existing.id),
                }

            maintenance = (
                db.query(WeeklyMaintenanceCost)
                .filter(WeeklyMaintenanceCost.week_start == week_start)
                .filter(WeeklyMaintenanceCost.week_end == week_end)
                .with_for_update()
                .first()
            )
            if maintenance is None:
                raise ValueError("Maintenance costs missing for target week")

            failed_goals = (
                db.query(Goal)
                .filter(Goal.finalized_at >= week_start)
                .filter(Goal.finalized_at < week_end)
                .filter(Goal.status == "finalized")
                .filter(Goal.verification_status == "failed")
                .all()
            )
            successful_goals = (
                db.query(Goal)
                .filter(Goal.finalized_at >= week_start)
                .filter(Goal.finalized_at < week_end)
                .filter(Goal.status == "finalized")
                .filter(Goal.verification_status == "completed")
                .all()
            )

            failed_by_type: dict[str, int] = {}
            for goal in failed_goals:
                type_key = str(goal.goal_type_id)
                failed_by_type[type_key] = failed_by_type.get(type_key, 0) + int(
                    goal.bounty_amount
                )

            successful_by_type: dict[str, list[Goal]] = {}
            for goal in successful_goals:
                type_key = str(goal.goal_type_id)
                successful_by_type.setdefault(type_key, []).append(goal)

            failed_pool_cents = int(sum(failed_by_type.values()))
            maintenance_fee_cents = int(maintenance.fee_amount_cents or 0)
            fee_to_apply_cents = min(maintenance_fee_cents, failed_pool_cents)

            fee_allocations_by_type = _allocate_weighted_payouts(
                net_pool_cents=fee_to_apply_cents,
                weighted_goals=[
                    (goal_type_id, pool_cents)
                    for goal_type_id, pool_cents in failed_by_type.items()
                    if pool_cents > 0
                ],
            )
            net_by_type = {
                goal_type_id: max(
                    pool_cents - int(fee_allocations_by_type.get(goal_type_id, 0)), 0
                )
                for goal_type_id, pool_cents in failed_by_type.items()
            }
            net_pool_cents = int(sum(net_by_type.values()))

            distribution = WeeklyPoolDistribution(
                week_start=week_start,
                week_end=week_end,
                failed_pool_cents=failed_pool_cents,
                maintenance_fee_cents=maintenance_fee_cents,
                net_pool_cents=net_pool_cents,
                successful_goals_count=len(successful_goals),
                distributed_total_cents=0,
                meta={
                    "failed_goal_count": len(failed_goals),
                    "successful_goal_count": len(successful_goals),
                    "failed_pool_by_goal_type": failed_by_type,
                    "maintenance_fee_by_goal_type": fee_allocations_by_type,
                    "net_pool_by_goal_type": net_by_type,
                },
            )
            db.add(distribution)
            db.flush()

            if net_pool_cents == 0 or len(successful_goals) == 0:
                return {
                    "status": "no_distribution",
                    "week_start": week_start.isoformat(),
                    "week_end": week_end.isoformat(),
                    "failed_pool_cents": failed_pool_cents,
                    "maintenance_fee_cents": maintenance_fee_cents,
                    "net_pool_cents": net_pool_cents,
                    "successful_goals_count": len(successful_goals),
                }

            distributed_total_cents = 0
            for goal_type_id, net_for_type_cents in net_by_type.items():
                if net_for_type_cents <= 0:
                    continue
                winners_for_type = successful_by_type.get(goal_type_id, [])
                if not winners_for_type:
                    continue

                payouts_by_goal_id = _allocate_weighted_payouts(
                    net_pool_cents=net_for_type_cents,
                    weighted_goals=[
                        (str(g.id), int(g.bounty_amount))
                        for g in winners_for_type
                        if int(g.bounty_amount) > 0
                    ],
                )

                for goal in winners_for_type:
                    payout_cents = int(payouts_by_goal_id.get(str(goal.id), 0))
                    if payout_cents <= 0:
                        continue

                    apply_bounty_ledger_entry(
                        user_id=goal.user_id,
                        goal_id=goal.id,
                        ledger_type="fund",
                        bounty_amount=payout_cents,
                        db=db,
                    )
                    item = WeeklyPoolDistributionItem(
                        distribution_id=distribution.id,
                        goal_id=goal.id,
                        user_id=goal.user_id,
                        goal_bounty_cents=int(goal.bounty_amount),
                        payout_cents=payout_cents,
                    )
                    db.add(item)
                    distributed_total_cents += payout_cents

            distribution.distributed_total_cents = distributed_total_cents

        return {
            "status": "ok",
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "failed_pool_cents": failed_pool_cents,
            "maintenance_fee_cents": maintenance_fee_cents,
            "net_pool_cents": net_pool_cents,
            "distributed_total_cents": distributed_total_cents,
            "successful_goals_count": len(successful_goals),
        }
    except Exception as exc:
        db.rollback()
        raise self.retry(exc=exc)
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=0, default_retry_delay=60)
def run_weekly_maintenance_and_distribution(self):
    result = chain(
        ingest_maintenance_costs_for_window.s(),
        distribute_weekly_pool.s(),
    ).apply_async()
    return {"chain_task_id": result.id}
