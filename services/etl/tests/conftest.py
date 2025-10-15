"""
Pytest fixtures for ETL tests.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.config import settings


@pytest.fixture(scope="function")
def db_session():
    """
    Create a test database session.
    
    Uses test database URL from environment or falls back to in-memory SQLite.
    Each test gets a fresh session with rolled-back transactions.
    """
    # Use test database if available, otherwise in-memory SQLite
    test_db_url = settings.database_url.replace(
        "agi_signposts", "agi_signpost_tracker_test"
    ) if "postgresql" in settings.database_url else "sqlite:///:memory:"
    
    engine = create_engine(test_db_url)
    Base.metadata.create_all(engine)
    
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.rollback()
    session.close()
    Base.metadata.drop_all(engine)
    engine.dispose()

