"""
Database configuration and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from app.logging_config import get_logger

logger = get_logger(__name__)

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://taskuser:taskpass@localhost:5432/taskdb"
)

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Create SessionLocal class for DB queries
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()


def get_db():
    """
    FastAPI dependency - provides DB session to endpoints
    Automatically closes after request
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables"""
    try:
        Base.metadata.create_all(bind=engine)
        # Hide password in logs
        safe_url = DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else "localhost"
        logger.info(f"Database tables created/verified at {safe_url}")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
        raise
