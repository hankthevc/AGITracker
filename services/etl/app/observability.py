"""Observability setup for ETL service."""
import logging
import sys

import structlog
from structlog.contextvars import merge_contextvars

from app.config import settings

# Try to import Sentry
try:
    import sentry_sdk
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False


def setup_logging():
    """Configure structured logging with structlog (JSON output)."""
    # Determine log level from settings
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )
    
    structlog.configure(
        processors=[
            merge_contextvars,  # Merges request_id from ContextVar
            structlog.stdlib.filter_by_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),  # Always use JSON for observability
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def setup_sentry():
    """Initialize Sentry SDK if configured."""
    if SENTRY_AVAILABLE and settings.sentry_dsn:
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.environment,
            traces_sample_rate=0.1,  # 10% of transactions
            profiles_sample_rate=0.1,
        )
        print("✓ Sentry initialized")
    elif settings.sentry_dsn and not SENTRY_AVAILABLE:
        print("⚠️  Sentry DSN provided but sentry-sdk not installed")
    else:
        print("ℹ️  Sentry not configured (no DSN provided)")


def get_logger(name: str):
    """Get a structured logger instance."""
    return structlog.get_logger(name)


# Initialize on import
setup_logging()
setup_sentry()

