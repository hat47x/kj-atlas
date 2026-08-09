"""enforce case-insensitive identity lookup uniqueness

Revision ID: 20260314_0005
Revises: 20260313_0004
Create Date: 2026-03-14 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260314_0005"
down_revision: str | None = "20260313_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _has_index(inspector: sa.Inspector, table_name: str, index_name: str) -> bool:
    return any(index["name"] == index_name for index in inspector.get_indexes(table_name))


def _has_case_insensitive_duplicates(bind: sa.Connection) -> bool:
    identities = sa.table(
        "user_identities",
        sa.column("provider"),
        sa.column("external_uid"),
    )
    duplicate_probe = (
        sa.select(sa.literal(1))
        .select_from(identities)
        .group_by(
            sa.func.lower(identities.c.provider),
            sa.func.lower(identities.c.external_uid),
        )
        .having(sa.func.count() > 1)
        .limit(1)
    )
    return bind.execute(duplicate_probe).first() is not None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("user_identities"):
        return

    if _has_case_insensitive_duplicates(bind):
        raise RuntimeError(
            "Detected case-insensitive duplicates in user_identities. "
            "Resolve duplicate (lower(provider), lower(external_uid)) rows before applying migration."
        )

    # MySQL-family fresh DDL gives these columns an explicit
    # utf8mb4_unicode_ci collation. The original composite unique constraint
    # therefore already enforces the same case-insensitive identity.
    if bind.dialect.name in {"mysql", "mariadb", "mssql"}:
        return

    if not _has_index(
        inspector, "user_identities", "uq_user_identities_provider_lower_external_uid"
    ):
        op.create_index(
            "uq_user_identities_provider_lower_external_uid",
            "user_identities",
            [sa.text("lower(provider)"), sa.text("lower(external_uid)")],
            unique=True,
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("user_identities"):
        return

    if bind.dialect.name in {"mysql", "mariadb", "mssql"}:
        return

    op.execute(sa.text("DROP INDEX IF EXISTS uq_user_identities_provider_lower_external_uid"))
