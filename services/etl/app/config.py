"""Configuration settings for the ETL service."""
import os
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/agi_signpost_tracker"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # OpenAI
    openai_api_key: str = ""
    
    # LLM Budget
    llm_budget_daily_usd: float = 20.0
    
    # Observability
    sentry_dsn: Optional[str] = None  # Legacy - use sentry_dsn_api instead
    sentry_dsn_api: Optional[str] = None
    sentry_dsn_web: Optional[str] = None
    healthchecks_url: Optional[str] = None
    log_level: str = "INFO"
    
    # Environment
    environment: str = "development"
    
    # Admin API Key
    admin_api_key: str = "change-me-in-production"
    
    # CORS
    cors_origins: str = "http://localhost:3000,https://*.vercel.app"
    
    # Caching
    index_cache_ttl_seconds: int = 120  # 2 minutes
    signposts_cache_ttl_seconds: int = 300  # 5 minutes
    evidence_cache_ttl_seconds: int = 180  # 3 minutes
    feed_cache_ttl_seconds: int = 300  # 5 minutes
    
    # Rate Limiting
    rate_limit_per_minute: int = 100  # Requests per minute per IP
    
    # Scrapers
    scrape_real: bool = False  # Use fixtures by default
    http_timeout_seconds: int = 20
    http_max_retries: int = 3
    http_backoff_base_seconds: int = 1
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

