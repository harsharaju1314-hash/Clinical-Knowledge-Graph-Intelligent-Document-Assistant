"""
Database session and connection management.
Supports PostgreSQL with transparent SQLite fallback for testing and lightweight local execution.
"""

import logging
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings
from app.core.models import Base

logger = logging.getLogger(__name__)

# Determine connection arguments based on database dialect
connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

try:
    engine = create_engine(
        settings.database_url,
        connect_args=connect_args,
        pool_pre_ping=True,
    )
except Exception as e:
    logger.warning(
        f"Failed to connect to primary DATABASE_URL '{settings.database_url}'. Falling back to local SQLite. Error: {e}"
    )
    fallback_url = "sqlite:///./clinical_kg.db"
    engine = create_engine(
        fallback_url,
        connect_args={"check_same_thread": False},
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified/created successfully.")


def get_db() -> Generator[Session, None, None]:
    """Dependency for providing database sessions per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
