"""add content-free generation deletion audit

Revision ID: 20260810_0019
Revises: 20260810_0018
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260810_0019"
down_revision: str | None = "20260810_0018"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_TABLE = "generation_deletion_audit_events"
_POLICY = "kj_atlas_generation_deletion_audit_tenant_isolation"
_TENANT_USING = "tenant_id = NULLIF(current_setting('kj_atlas.tenant_id', true), '')"


def upgrade() -> None:
    op.create_table(
        _TABLE,
        sa.Column("event_id", sa.Text(), nullable=False),
        sa.Column("tenant_id", sa.Text(), nullable=False),
        sa.Column("target_kind", sa.Text(), nullable=False),
        sa.Column("target_ref", sa.Text(), nullable=False),
        sa.Column("storage_backend", sa.Text(), nullable=True),
        sa.Column("action", sa.Text(), nullable=False),
        sa.Column("outcome", sa.Text(), nullable=False),
        sa.Column("executor_ref", sa.Text(), nullable=False),
        sa.Column("occurred_at", sa.Text(), nullable=False),
        sa.CheckConstraint(
            "action IN ('revision_gc.delete', 'blob_gc.delete')",
            name="ck_generation_deletion_audit_action",
        ),
        sa.CheckConstraint(
            "outcome IN ('deleted', 'not_found', 'failed')",
            name="ck_generation_deletion_audit_outcome",
        ),
        sa.CheckConstraint(
            "target_kind IN ('revision', 'blob')",
            name="ck_generation_deletion_audit_target_kind",
        ),
        sa.CheckConstraint(
            "(target_kind = 'revision' AND action = 'revision_gc.delete' "
            "AND storage_backend IS NULL) OR "
            "(target_kind = 'blob' AND action = 'blob_gc.delete' "
            "AND storage_backend IS NOT NULL)",
            name="ck_generation_deletion_audit_target_shape",
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("event_id"),
    )
    op.create_index(
        "ix_generation_deletion_audit_tenant_occurred",
        _TABLE,
        ["tenant_id", "occurred_at"],
    )
    if op.get_bind().dialect.name == "postgresql":
        op.execute(sa.text(f"ALTER TABLE {_TABLE} ENABLE ROW LEVEL SECURITY"))
        op.execute(sa.text(f"ALTER TABLE {_TABLE} FORCE ROW LEVEL SECURITY"))
        op.execute(
            sa.text(
                f"CREATE POLICY {_POLICY} ON {_TABLE} "
                f"USING ({_TENANT_USING}) WITH CHECK ({_TENANT_USING})"
            )
        )


def downgrade() -> None:
    if op.get_bind().dialect.name == "postgresql":
        op.execute(sa.text(f"DROP POLICY IF EXISTS {_POLICY} ON {_TABLE}"))
    op.drop_index("ix_generation_deletion_audit_tenant_occurred", table_name=_TABLE)
    op.drop_table(_TABLE)
