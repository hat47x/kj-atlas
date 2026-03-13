"""create merge_decision_logs table

Revision ID: 20260313_0003
Revises: 20260303_0002
Create Date: 2026-03-13 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260313_0003"
down_revision: str | None = "20260303_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("merge_decision_logs"):
        op.create_table(
            "merge_decision_logs",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("doc_id", sa.Text(), nullable=False),
            sa.Column("decision_id", sa.Text(), nullable=False),
            sa.Column("group_id", sa.Text(), nullable=False),
            sa.Column("snapshot_version", sa.Text(), nullable=False),
            sa.Column("decided_at", sa.Text(), nullable=False),
            sa.Column("payload_json", sa.Text(), nullable=False),
            sa.ForeignKeyConstraint(["doc_id"], ["documents.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("doc_id", "decision_id", name="uq_merge_decision_logs_doc_decision"),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("merge_decision_logs"):
        op.drop_table("merge_decision_logs")
