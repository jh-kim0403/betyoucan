import os
from celery import Celery
from celery.schedules import crontab
from src.config import settings


rabbitmq_url = settings.rabbitmq_url
database_url = settings.database_url
celery_app = Celery(
    "betyoucan",
    broker=settings.rabbitmq_url,
    backend=f"db+{settings.database_url}",
    include=[
        "src.tasks.deadline_tasks",
        "src.tasks.distribution_tasks",
        "src.tasks.evaluations",
        "src.tasks.maintenance_cost_tasks",
        "src.tasks.quiz_tasks",
        "src.tasks.verification_cleanup",
    ],
)

celery_app.conf.update(
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_reject_on_worker_lost=True,
)


celery_app.conf.beat_schedule = {
    "sweep-overdue-goals-every-minute": {
        "task": "src.tasks.deadline_tasks.sweep_overdue_goals",
        "schedule": crontab(minute="*"),
    },
    "cleanup-abandoned-photo-verifications-hourly": {
        "task": "src.tasks.verification_cleanup.cleanup_abandoned_photo_verifications",
        "schedule": crontab(minute=0, hour="*/1"),
    },
    "run-weekly-maintenance-and-distribution": {
        "task": "src.tasks.distribution_tasks.run_weekly_maintenance_and_distribution",
        "schedule": crontab(minute=5, hour=0, day_of_week="mon"),
    },
}
