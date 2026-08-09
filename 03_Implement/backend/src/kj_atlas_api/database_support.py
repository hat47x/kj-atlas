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
    ),
    "postgresql": DatabaseSupport(
        backend="postgresql",
        family="postgresql",
        support_level="verified",
        migration_strategy="constraint-ddl",
        shared_schema_saas=True,
        inline_content="verified",
        atomic_primary_key_replacement=False,
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
    ),
    "mariadb": DatabaseSupport(
        backend="mariadb",
        family="mysql",
        support_level="verified",
        migration_strategy="constraint-ddl",
        shared_schema_saas=False,
        inline_content="verified",
        atomic_primary_key_replacement=False,
    ),
    "mssql": DatabaseSupport(
        backend="mssql",
        family="mssql",
        support_level="verified",
        migration_strategy="constraint-ddl",
        shared_schema_saas=False,
        inline_content="verified",
        atomic_primary_key_replacement=False,
    ),
    "oracle": DatabaseSupport(
        backend="oracle",
        family="oracle",
        support_level="candidate",
        migration_strategy="unimplemented",
        shared_schema_saas=False,
        inline_content="candidate",
        atomic_primary_key_replacement=False,
    ),
    "cockroachdb": DatabaseSupport(
        backend="cockroachdb",
        family="cockroachdb",
        support_level="verified",
        migration_strategy="constraint-ddl",
        shared_schema_saas=False,
        inline_content="verified",
        atomic_primary_key_replacement=True,
    ),
}


def database_support_for_backend(backend: str) -> DatabaseSupport:
    normalized_backend = backend.strip().lower()
    support = _DATABASE_SUPPORT_BY_BACKEND.get(normalized_backend)
    if support is None:
        raise ValueError(
            f"Unsupported database backend: {normalized_backend or '<empty>'}. "
            "Verified backends: sqlite, postgresql, mysql, mariadb, mssql, cockroachdb"
        )
    return support


def database_support_for_url(database_url: str) -> DatabaseSupport:
    try:
        backend = make_url(database_url).get_backend_name()
    except Exception as error:
        raise ValueError("KJ_ATLAS_DATABASE_URL must be a valid SQLAlchemy URL") from error
    return database_support_for_backend(backend)


def require_verified_database_url(database_url: str) -> DatabaseSupport:
    support = database_support_for_url(database_url)
    if not support.is_verified:
        raise ValueError(
            f"Database backend '{support.backend}' is a candidate, not a verified runtime. "
            "Its identifier types and Alembic migration matrix must be completed before use. "
            "Verified backends: sqlite, postgresql, mysql, mariadb, mssql, cockroachdb"
        )
    return support


def normalize_sync_database_url(database_url: str) -> str:
    """Normalize supported async URLs for the synchronous SQLAlchemy stack."""
    require_verified_database_url(database_url)
    url: URL = make_url(database_url)

    if url.drivername == "sqlite+aiosqlite":
        url = url.set(drivername="sqlite")
    elif url.drivername == "postgresql+asyncpg":
        url = url.set(drivername="postgresql+psycopg")

    # URL.__str__ masks passwords, which would pass literal *** to the driver.
    return url.render_as_string(hide_password=False)


def alembic_config_database_url(database_url: str) -> str:
    """Return a normalized URL escaped for ConfigParser interpolation."""
    return normalize_sync_database_url(database_url).replace("%", "%%")


def registered_database_support() -> tuple[DatabaseSupport, ...]:
    """Stable, read-only registry view for contract tests and documentation tooling."""
    return tuple(_DATABASE_SUPPORT_BY_BACKEND.values())
