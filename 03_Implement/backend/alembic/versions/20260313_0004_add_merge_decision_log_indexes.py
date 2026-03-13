"""add indexes for merge decision log lookup paths

Revision ID: 20260313_0004
Revises: 20260313_0003
Create Date: 2026-03-13 00:40:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260313_0004"
down_revision: str | None = "20260313_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _has_index(inspector: sa.Inspector, table_name: str, index_name: str) -> bool:
    return any(index["name"] == index_name for index in inspector.get_indexes(table_name))


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("merge_decision_logs"):
        return

    if not _has_index(inspector, "merge_decision_logs", "ix_merge_decision_logs_doc_group_id"):
        op.create_index(
            "ix_merge_decision_logs_doc_group_id",
            "merge_decision_logs",
            ["doc_id", "group_id", "id"],
            unique=False,
        )

    if not _has_index(inspector, "merge_decision_logs", "ix_merge_decision_logs_doc_snapshot_id"):
        op.create_index(
            "ix_merge_decision_logs_doc_snapshot_id",
            "merge_decision_logs",
            ["doc_id", "snapshot_version", "id"],
            unique=False,
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("merge_decision_logs"):
        return

    if _has_index(inspector, "merge_decision_logs", "ix_merge_decision_logs_doc_snapshot_id"):
        op.drop_index("ix_merge_decision_logs_doc_snapshot_id", table_name="merge_decision_logs")

    if _has_index(inspector, "merge_decision_logs", "ix_merge_decision_logs_doc_group_id"):
        op.drop_index("ix_merge_decision_logs_doc_group_id", table_name="merge_decision_logs")
