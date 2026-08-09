"""add index on tenant_memberships.user_id

Revision ID: 20260720_0013
Revises: 20260720_0012
Create Date: 2026-07-20 00:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260720_0013"
down_revision: str | None = "20260720_0012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TABLE_NAME = "tenant_memberships"
INDEX_NAME = "ix_tenant_memberships_user_id"
MYSQL_FK_KEEP_INDEX = "ix_tenant_memberships_user_id_fk_keep"


def _has_index(inspector: sa.Inspector, table_name: str, index_name: str) -> bool:
    return any(index["name"] == index_name for index in inspector.get_indexes(table_name))


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table(TABLE_NAME):
        return

    if not _has_index(inspector, TABLE_NAME, INDEX_NAME):
        op.create_index(
            INDEX_NAME,
            TABLE_NAME,
            ["user_id"],
            unique=False,
        )
    if bind.dialect.name in {"mysql", "mariadb"} and _has_index(
        sa.inspect(bind), TABLE_NAME, MYSQL_FK_KEEP_INDEX
    ):
        op.drop_index(MYSQL_FK_KEEP_INDEX, table_name=TABLE_NAME)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table(TABLE_NAME):
        return

    if _has_index(inspector, TABLE_NAME, INDEX_NAME):
        if bind.dialect.name in {"mysql", "mariadb"} and not _has_index(
            inspector, TABLE_NAME, MYSQL_FK_KEEP_INDEX
        ):
            op.create_index(
                MYSQL_FK_KEEP_INDEX,
                TABLE_NAME,
                ["user_id"],
                unique=False,
            )
        op.drop_index(INDEX_NAME, table_name=TABLE_NAME)
