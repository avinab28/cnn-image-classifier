import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Database URL (default to local Postgres for development)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/cnndb")

# Some providers emit the legacy "postgres://" scheme; SQLAlchemy expects
# "postgresql://", so normalize it here.
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create engine and session factory (SQLAlchemy 1.4+/2.0 compatible)
engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
Base = declarative_base()


def get_db():
    """Yield a database session, closing it after use (dependency for FastAPI).

    Usage:
        db = next(get_db())  # for simple scripts
        with next(get_db()) as db:  # or use as dependency in FastAPI
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()