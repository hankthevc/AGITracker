"""Healthchecks.io integration for monitoring ETL tasks."""
import httpx
from celery import shared_task

from app.celery_app import celery_app
from app.config import settings


@celery_app.task(name="app.tasks.healthchecks.ping_healthcheck")
def ping_healthcheck(status: str = "success"):
    """
    Ping healthchecks.io after ETL cycle completion.
    
    Args:
        status: "success" or "fail"
    """
    if not settings.healthchecks_url:
        return {"status": "skipped", "reason": "no healthchecks_url configured"}
    
    url = settings.healthchecks_url
    if status == "fail":
        url = f"{url}/fail"
    
    try:
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
        return {"status": "ok", "pinged": url}
    except Exception as e:
        return {"status": "error", "error": str(e)}

