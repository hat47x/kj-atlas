from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import Session, sessionmaker

from kj_atlas_api.settings import settings


def _normalize_database_url(database_url: str) -> str:
    """Normalize async SQLAlchemy URLs to sync drivers for this Phase 1 sync stack."""
    url = make_url(database_url)

    if url.drivername == "sqlite+aiosqlite":
        return str(url.set(drivername="sqlite"))

    if url.drivername == "postgresql+asyncpg":
        return str(url.set(drivername="postgresql+psycopg"))

    return database_url


normalized_database_url = _normalize_database_url(settings.database_url)
is_sqlite = normalized_database_url.startswith("sqlite")
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
