"""LLM budget tracking and management."""
import redis
from datetime import datetime

from app.config import settings

redis_client = redis.from_url(settings.redis_url)

BUDGET_KEY = "llm_spend_today_usd"
BUDGET_DATE_KEY = "llm_spend_date"


def get_daily_spend() -> float:
    """Get current daily LLM spend."""
    # Check if date has changed (reset at midnight UTC)
    today = datetime.utcnow().date().isoformat()
    stored_date = redis_client.get(BUDGET_DATE_KEY)
    
    if stored_date is None or stored_date.decode() != today:
        # New day - reset
        redis_client.set(BUDGET_KEY, "0.0")
        redis_client.set(BUDGET_DATE_KEY, today)
        return 0.0
    
    spend = redis_client.get(BUDGET_KEY)
    return float(spend) if spend else 0.0


def add_spend(amount: float):
    """Add to daily LLM spend."""
    current = get_daily_spend()
    new_total = current + amount
    redis_client.set(BUDGET_KEY, str(new_total))
    return new_total


def can_spend(amount: float) -> bool:
    """Check if we can spend this amount without exceeding budget."""
    current = get_daily_spend()
    return (current + amount) <= settings.llm_budget_daily_usd


def get_remaining_budget() -> float:
    """Get remaining budget for today."""
    current = get_daily_spend()
    return max(0.0, settings.llm_budget_daily_usd - current)

