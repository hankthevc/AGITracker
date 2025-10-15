"""Celery application configuration for ETL tasks."""
from celery import Celery
from celery.schedules import crontab

from app.config import settings

# Create Celery app
celery_app = Celery(
    "agi_tracker_etl",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks.fetch_feeds", "app.tasks.extract_claims", "app.tasks.snap_index"],
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Beat schedule (periodic tasks)
# Note: Times staggered by 3-8 minutes to prevent thundering herd
celery_app.conf.beat_schedule = {
    "fetch-feeds-daily": {
        "task": "app.tasks.fetch_feeds.fetch_all_feeds",
        "schedule": crontab(hour=6, minute=3),  # 6:03 AM UTC daily
    },
    "fetch-swebench": {
        "task": "fetch_swebench",
        "schedule": crontab(hour=7, minute=12),  # 7:12 AM UTC daily
    },
    "fetch-osworld": {
        "task": "fetch_osworld",
        "schedule": crontab(hour=7, minute=28),  # 7:28 AM UTC daily
    },
    "fetch-webarena": {
        "task": "fetch_webarena",
        "schedule": crontab(hour=7, minute=41),  # 7:41 AM UTC daily
    },
    "fetch-gpqa": {
        "task": "fetch_gpqa",
        "schedule": crontab(hour=7, minute=54),  # 7:54 AM UTC daily
    },
    "snap-index-daily": {
        "task": "app.tasks.snap_index.compute_daily_snapshot",
        "schedule": crontab(hour=8, minute=5),  # 8:05 AM UTC daily (after all fetches)
    },
    # Inputs & Security tasks (weekly on Monday)
    "seed-inputs": {
        "task": "seed_inputs",
        "schedule": crontab(hour=8, minute=17, day_of_week=1),  # Monday 8:17 AM UTC
    },
    "security-maturity": {
        "task": "security_maturity",
        "schedule": crontab(hour=8, minute=32, day_of_week=1),  # Monday 8:32 AM UTC
    },
    # Weekly digest
    "digest-weekly": {
        "task": "app.tasks.snap_index.generate_weekly_digest",
        "schedule": crontab(day_of_week=0, hour=8, minute=8),  # Sunday 8:08 AM UTC
    },
}

if __name__ == "__main__":
    celery_app.start()

