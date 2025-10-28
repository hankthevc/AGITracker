"""Configuration settings for the ETL service."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Database
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/agi_signpost_tracker"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # OpenAI
    openai_api_key: str = ""

    # Anthropic (Sprint 7.3)
    anthropic_api_key: str = ""

    # LLM Budget
    llm_budget_daily_usd: float = 20.0

    # Observability
    sentry_dsn: str | None = None  # Legacy - use sentry_dsn_api instead
    sentry_dsn_api: str | None = None
    sentry_dsn_web: str | None = None
    healthchecks_url: str | None = None
    log_level: str = "INFO"

    # Environment
    environment: str = "development"

    # Admin API Key
    admin_api_key: str = "change-me-in-production"

    # CORS (comma-separated, no wildcards)
    cors_origins: str = "http://localhost:3000,https://agi-tracker.vercel.app"

    # Caching
    index_cache_ttl_seconds: int = 120  # 2 minutes
    signposts_cache_ttl_seconds: int = 300  # 5 minutes
    evidence_cache_ttl_seconds: int = 180  # 3 minutes
    feed_cache_ttl_seconds: int = 300  # 5 minutes

    # Rate Limiting
    rate_limit_per_minute: int = 100  # Requests per minute per IP

    # Scrapers
    scrape_real: bool = True  # Enable live scraping by default (Sprint 7.1)
    http_timeout_seconds: int = 20
    http_max_retries: int = 3
    http_backoff_base_seconds: int = 1

    # LLM Mapping
    enable_llm_mapping: bool = False  # Enable LLM-powered event mapping (requires OPENAI_API_KEY)

    # Operations
    dry_run: bool = False  # If true, skip DB writes (for testing/debugging)

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

