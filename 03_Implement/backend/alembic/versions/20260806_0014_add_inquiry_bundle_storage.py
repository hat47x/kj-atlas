"""add tenant-scoped opaque inquiry bundle storage

Revision ID: 20260806_0014
Revises: 20260720_0013
Create Date: 2026-08-06 00:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260806_0014"
down_revision: str | None = "20260720_0013"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_BUNDLE_TABLE = "inquiry_bundles"
_AUDIT_TABLE = "inquiry_bundle_deletion_audit_events"
_BUNDLE_POLICY = "kj_atlas_inquiry_bundles_tenant_isolation"
_AUDIT_POLICY = "kj_atlas_inquiry_bundle_deletion_audit_tenant_isolation"
_TENANT_USING = "tenant_id = NULLIF(current_setting('kj_atlas.tenant_id', true), '')"


def _enable_rls(table_name: str, policy_name: str) -> None:
    op.execute(sa.text(f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY"))
    op.execute(sa.text(f"ALTER TABLE {table_name} FORCE ROW LEVEL SECURITY"))
    op.execute(
        sa.text(
            f"CREATE POLICY {policy_name} ON {table_name} "
            f"USING ({_TENANT_USING}) WITH CHECK ({_TENANT_USING})"
        )
    )


def upgrade() -> None:
    op.create_table(
        _BUNDLE_TABLE,
        sa.Column("tenant_id", sa.Text(), nullable=False),
        sa.Column("journey_id", sa.Text(), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("tenant_id", "journey_id"),
    )
    op.create_table(
        _AUDIT_TABLE,
        sa.Column("event_id", sa.Text(), nullable=False),
        sa.Column("tenant_id", sa.Text(), nullable=False),
        sa.Column("journey_id", sa.Text(), nullable=False),
        sa.Column("principal_id", sa.Text(), nullable=False),
        sa.Column("action", sa.Text(), nullable=False),
        sa.Column("outcome", sa.Text(), nullable=False),
        sa.Column("occurred_at", sa.Text(), nullable=False),
        sa.CheckConstraint(
            "action = 'inquiry_bundle.delete'",
            name="ck_inquiry_bundle_deletion_audit_action",
        ),
        sa.CheckConstraint(
            "outcome = 'deleted'",
            name="ck_inquiry_bundle_deletion_audit_outcome",
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("event_id"),
    )
    op.create_index(
        "ix_inquiry_bundle_deletion_audit_tenant_occurred",
        _AUDIT_TABLE,
        ["tenant_id", "occurred_at"],
    )
    if op.get_bind().dialect.name == "postgresql":
        _enable_rls(_BUNDLE_TABLE, _BUNDLE_POLICY)
        _enable_rls(_AUDIT_TABLE, _AUDIT_POLICY)


def downgrade() -> None:
    if op.get_bind().dialect.name == "postgresql":
        op.execute(sa.text(f"DROP POLICY IF EXISTS {_AUDIT_POLICY} ON {_AUDIT_TABLE}"))
        op.execute(sa.text(f"DROP POLICY IF EXISTS {_BUNDLE_POLICY} ON {_BUNDLE_TABLE}"))
    op.drop_table(_AUDIT_TABLE)
    op.drop_table(_BUNDLE_TABLE)
