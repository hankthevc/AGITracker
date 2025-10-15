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
    sentry_dsn: Optional[str] = None
    healthchecks_url: Optional[str] = None
    
    # Environment
    environment: str = "development"
    
    # Admin API Key
    admin_api_key: str = "change-me-in-production"
    
    # CORS
    cors_origins: str = "http://localhost:3000,https://*.vercel.app"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

