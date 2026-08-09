from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from sqlalchemy.engine import URL, make_url


DatabaseSupportLevel = Literal["verified", "candidate"]
MigrationStrategy = Literal["sqlite-rebuild", "constraint-ddl", "unimplemented"]
InlineContentSupport = Literal["verified", "candidate", "unsupported"]


@dataclass(frozen=True)
class DatabaseSupport:
    """One registry for runtime, migration, and deployment database decisions."""

    backend: str
    family: str
    support_level: DatabaseSupportLevel
    migration_strategy: MigrationStrategy
    shared_schema_saas: bool
    inline_content: InlineContentSupport
    atomic_primary_key_replacement: bool
    sync_drivername: str
    accepted_drivernames: tuple[str, ...]
    optional_dependency: str | None
    test_marker: str | None

    @property
    def is_verified(self) -> bool:
        return self.support_level == "verified"


_DATABASE_SUPPORT_BY_BACKEND: dict[str, DatabaseSupport] = {
    "sqlite": DatabaseSupport(
        backend="sqlite",
        family="sqlite",
        support_level="verified",
        migration_strategy="sqlite-rebuild",
        shared_schema_saas=False,
        inline_content="verified",
        atomic_primary_key_replacement=False,
        sync_drivername="sqlite",
        accepted_drivernames=("sqlite", "sqlite+pysqlite", "sqlite+aiosqlite"),
        optional_dependency=None,
        test_marker=None,
    ),
    "postgresql": DatabaseSupport(
        backend="postgresql",
        family="postgresql",
        support_level="verified",
        migration_strategy="constraint-ddl",
        shared_schema_saas=True,
        inline_content="verified",
        atomic_primary_key_replacement=False,
        sync_drivername="postgresql+psycopg",
        accepted_drivernames=(
            "postgresql",
            "postgresql+psycopg",
            "postgresql+asyncpg",
        ),
        optional_dependency="postgres",
        test_marker="postgres",
    ),
    # Verified and candidate entries stay together so capability decisions do
    # not spread across settings, runtime, migrations, and documentation.
    "mysql": DatabaseSupport(
        backend="mysql",
        family="mysql",
        support_level="verified",
        migration_strategy="constraint-ddl",
        shared_schema_saas=False,
        inline_content="verified",
        atomic_primary_key_replacement=False,
        sync_drivername="mysql+pymysql",
        accepted_drivernames=("mysql", "mysql+pymysql"),
        optional_dependency="mysql",
        test_marker="mysql",
    ),
    "mariadb": DatabaseSupport(
        backend="mariadb",
        family="mysql",
        support_level="verified",
        migration_strategy="constraint-ddl",
        shared_schema_saas=False,
        inline_content="verified",
        atomic_primary_key_replacement=False,
        sync_drivername="mariadb+pymysql",
        accepted_drivernames=("mariadb", "mariadb+pymysql"),
        optional_dependency="mysql",
        test_marker="mysql",
    ),
    "mssql": DatabaseSupport(
        backend="mssql",
        family="mssql",
        support_level="verified",
        migration_strategy="constraint-ddl",
        shared_schema_saas=False,
        inline_content="verified",
        atomic_primary_key_replacement=False,
        sync_drivername="mssql+pymssql",
        accepted_drivernames=("mssql", "mssql+pymssql"),
        optional_dependency="mssql",
        test_marker="mssql",
    ),
    "oracle": DatabaseSupport(
        backend="oracle",
        family="oracle",
        support_level="verified",
        migration_strategy="constraint-ddl",
        shared_schema_saas=False,
        inline_content="verified",
        atomic_primary_key_replacement=False,
        sync_drivername="oracle+oracledb",
        accepted_drivernames=("oracle", "oracle+oracledb"),
        optional_dependency="oracle",
        test_marker="oracle",
    ),
    "cockroachdb": DatabaseSupport(
        backend="cockroachdb",
        family="cockroachdb",
        support_level="verified",
        migration_strategy="constraint-ddl",
        shared_schema_saas=False,
        inline_content="verified",
        atomic_primary_key_replacement=True,
        sync_drivername="cockroachdb+psycopg",
        accepted_drivernames=("cockroachdb", "cockroachdb+psycopg"),
        optional_dependency="cockroachdb",
        test_marker="cockroachdb",
    ),
}


def database_support_for_backend(backend: str) -> DatabaseSupport:
    normalized_backend = backend.strip().lower()
    support = _DATABASE_SUPPORT_BY_BACKEND.get(normalized_backend)
    if support is None:
        raise ValueError(
            f"Unsupported database backend: {normalized_backend or '<empty>'}. "
            f"Verified backends: {', '.join(verified_database_backends())}"
        )
    return support


def database_support_for_url(database_url: str) -> DatabaseSupport:
    try:
        backend = make_url(database_url).get_backend_name()
    except Exception as error:
        raise ValueError("KJ_ATLAS_DATABASE_URL must be a valid SQLAlchemy URL") from error
    return database_support_for_backend(backend)


def require_verified_database_url(database_url: str) -> DatabaseSupport:
    try:
        url = make_url(database_url)
    except Exception as error:
        raise ValueError("KJ_ATLAS_DATABASE_URL must be a valid SQLAlchemy URL") from error
    support = database_support_for_backend(url.get_backend_name())
    if not support.is_verified:
        raise ValueError(
            f"Database backend '{support.backend}' is a candidate, not a verified runtime. "
            "Its identifier types and Alembic migration matrix must be completed before use. "
            f"Verified backends: {', '.join(verified_database_backends())}"
        )
    if url.drivername not in support.accepted_drivernames:
        raise ValueError(
            f"Unsupported SQLAlchemy driver for database backend '{support.backend}'. "
            "Accepted driver names: "
            f"{', '.join(support.accepted_drivernames)}"
        )
    return support


def normalize_sync_database_url(database_url: str) -> str:
    """Normalize supported async URLs for the synchronous SQLAlchemy stack."""
    support = require_verified_database_url(database_url)
    url: URL = make_url(database_url)
    url = url.set(drivername=support.sync_drivername)

    # URL.__str__ masks passwords, which would pass literal *** to the driver.
    return url.render_as_string(hide_password=False)


def alembic_config_database_url(database_url: str) -> str:
    """Return a normalized URL escaped for ConfigParser interpolation."""
    return normalize_sync_database_url(database_url).replace("%", "%%")


def registered_database_support() -> tuple[DatabaseSupport, ...]:
    """Stable, read-only registry view for contract tests and documentation tooling."""
    return tuple(_DATABASE_SUPPORT_BY_BACKEND.values())


def verified_database_backends() -> tuple[str, ...]:
    """Return verified backend names in the registry's stable presentation order."""
    return tuple(
        support.backend
        for support in _DATABASE_SUPPORT_BY_BACKEND.values()
        if support.is_verified
    )
