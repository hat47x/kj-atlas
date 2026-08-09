from __future__ import annotations

import pytest
from pydantic import ValidationError

from kj_atlas_api.database_support import (
    database_support_for_backend,
    database_support_for_url,
    normalize_sync_database_url,
    registered_database_support,
    require_verified_database_url,
)
from kj_atlas_api.settings import Settings


def test_verified_database_capabilities_are_explicit() -> None:
    sqlite = database_support_for_backend("sqlite")
    postgres = database_support_for_backend("postgresql")

    assert sqlite.is_verified is True
    assert sqlite.migration_strategy == "sqlite-rebuild"
    assert sqlite.shared_schema_saas is False
    assert sqlite.inline_content == "verified"
    assert postgres.is_verified is True
    assert postgres.migration_strategy == "constraint-ddl"
    assert postgres.shared_schema_saas is True
    assert postgres.inline_content == "verified"


@pytest.mark.parametrize(
    ("url", "backend", "family"),
    [
        ("mysql+pymysql://user:secret@db/kj_atlas", "mysql", "mysql"),
        ("mariadb+pymysql://user:secret@db/kj_atlas", "mariadb", "mysql"),
        ("mssql+pyodbc://user:secret@db/kj_atlas", "mssql", "mssql"),
        ("oracle+oracledb://user:secret@db/kj_atlas", "oracle", "oracle"),
        ("cockroachdb://user:secret@db/kj_atlas", "cockroachdb", "cockroachdb"),
    ],
)
def test_future_databases_are_registered_without_being_enabled(
    url: str,
    backend: str,
    family: str,
) -> None:
    support = database_support_for_url(url)

    assert support.backend == backend
    assert support.family == family
    assert support.is_verified is False
    assert support.migration_strategy == "unimplemented"
    assert support.shared_schema_saas is False
    assert support.inline_content == "candidate"

    with pytest.raises(ValueError, match="candidate, not a verified runtime"):
        require_verified_database_url(url)


def test_unknown_database_is_rejected_without_echoing_credentials() -> None:
    with pytest.raises(ValueError) as captured:
        require_verified_database_url("db2://sensitive-user:secret-password@db/kj_atlas")

    message = str(captured.value)
    assert "Unsupported database backend: db2" in message
    assert "sensitive-user" not in message
    assert "secret-password" not in message


def test_malformed_database_url_is_rejected_with_stable_error() -> None:
    with pytest.raises(ValueError, match="must be a valid SQLAlchemy URL"):
        require_verified_database_url("not a database url")


def test_sync_normalization_preserves_encoded_credentials() -> None:
    assert normalize_sync_database_url("sqlite+aiosqlite:///./kj_atlas.db") == (
        "sqlite:///./kj_atlas.db"
    )
    assert (
        normalize_sync_database_url("postgresql+asyncpg://user:p%40ss@db:5432/kj_atlas")
        == "postgresql+psycopg://user:p%40ss@db:5432/kj_atlas"
    )


def test_registry_has_no_duplicate_backends() -> None:
    registered = registered_database_support()
    assert len({item.backend for item in registered}) == len(registered)


def test_settings_rejects_candidate_before_engine_creation(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv(
        "KJ_ATLAS_DATABASE_URL",
        "mysql+pymysql://sensitive-user:secret-password@db/kj_atlas",
    )

    with pytest.raises(ValidationError) as captured:
        Settings(_env_file=None)

    message = str(captured.value)
    assert "candidate, not a verified runtime" in message
    assert "sensitive-user" not in message
    assert "secret-password" not in message
