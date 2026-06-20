from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import Session, sessionmaker

from kj_atlas_api.settings import settings


def _normalize_database_url(database_url: str) -> str:
    """Normalize async SQLAlchemy URLs to sync drivers for this Phase 1 sync stack."""
    url = make_url(database_url)

    # NOTE: use render_as_string(hide_password=False), not str(url). SQLAlchemy's
    # str(URL) masks the password as "***", which would otherwise be passed verbatim
    # to the driver and cause "password authentication failed" on the postgres path.
    if url.drivername == "sqlite+aiosqlite":
        return url.set(drivername="sqlite").render_as_string(hide_password=False)

    if url.drivername == "postgresql+asyncpg":
        return url.set(drivername="postgresql+psycopg").render_as_string(hide_password=False)

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
