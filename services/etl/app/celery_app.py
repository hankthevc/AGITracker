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
celery_app.conf.beat_schedule = {
    "fetch-feeds-daily": {
        "task": "app.tasks.fetch_feeds.fetch_all_feeds",
        "schedule": crontab(hour=6, minute=0),  # 6 AM UTC daily
    },
    "snap-index-daily": {
        "task": "app.tasks.snap_index.compute_daily_snapshot",
        "schedule": crontab(hour=7, minute=0),  # 7 AM UTC daily (after fetch)
    },
    "digest-weekly": {
        "task": "app.tasks.snap_index.generate_weekly_digest",
        "schedule": crontab(day_of_week=0, hour=8, minute=0),  # Sunday 8 AM UTC
    },
}

if __name__ == "__main__":
    celery_app.start()

