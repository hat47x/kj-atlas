"""Regression tests for kj_atlas_api.db._normalize_database_url.

Guards against the SQLAlchemy str(URL) password-masking bug: str(url) renders the
password as "***", which (when fed back to create_engine / alembic) caused
"password authentication failed" on the postgres+asyncpg Docker path. The fix uses
render_as_string(hide_password=False). These tests run on the default sqlite stack,
so they catch the regression without needing a live PostgreSQL.
"""

from sqlalchemy.engine.url import make_url

from kj_atlas_api.db import _normalize_database_url


def test_postgres_asyncpg_normalizes_driver_and_preserves_password() -> None:
    result = _normalize_database_url("postgresql+asyncpg://kj_atlas:s3cr3t@db:5432/kj_atlas")

    assert result.startswith("postgresql+psycopg://")
    assert "s3cr3t" in result
    assert "***" not in result


def test_postgres_asyncpg_preserves_password_with_special_chars() -> None:
    # URL-reserved characters in the password must survive the normalization round-trip.
    result = _normalize_database_url("postgresql+asyncpg://kj_atlas:p%40ss%2Fword@db:5432/kj_atlas")

    parsed = make_url(result)
    assert parsed.drivername == "postgresql+psycopg"
    assert parsed.password == "p@ss/word"
    assert "***" not in result


def test_sqlite_aiosqlite_maps_to_sync_sqlite() -> None:
    result = _normalize_database_url("sqlite+aiosqlite:///./kj_atlas.db")

    assert result.startswith("sqlite://")


def test_already_sync_url_passes_through_unchanged() -> None:
    original = "postgresql+psycopg://kj_atlas:s3cr3t@db:5432/kj_atlas"

    assert _normalize_database_url(original) == original
