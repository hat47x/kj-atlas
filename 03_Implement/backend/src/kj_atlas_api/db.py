from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from kj_atlas_api.database_support import (
    database_support_for_url,
    normalize_sync_database_url,
)
from kj_atlas_api.settings import settings


def _normalize_database_url(database_url: str) -> str:
    """Backward-compatible import path for migration and test callers."""
    return normalize_sync_database_url(database_url)


normalized_database_url = _normalize_database_url(settings.database_url)
database_support = database_support_for_url(normalized_database_url)
is_sqlite = database_support.backend == "sqlite"
engine = create_engine(
    normalized_database_url,
    connect_args={"check_same_thread": False} if is_sqlite else {},
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def init_db() -> None:
    """Keep startup DB initialization non-failing. Schema is managed by Alembic."""
    return None


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
