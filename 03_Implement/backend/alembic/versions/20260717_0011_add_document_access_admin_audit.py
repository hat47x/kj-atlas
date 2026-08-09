"""add tenant-scoped document access administration audit

Revision ID: 20260717_0011
Revises: 20260717_0010
Create Date: 2026-07-17 12:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260717_0011"
down_revision: str | None = "20260717_0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

POLICY_NAME = "kj_atlas_document_access_admin_audit_tenant_isolation"
TENANT_EXPRESSION = "tenant_id = NULLIF(current_setting('kj_atlas.tenant_id', true), '')"


def upgrade() -> None:
    op.create_table(
        "document_access_admin_audit_events",
        sa.Column("event_id", sa.Text(), nullable=False),
        sa.Column("tenant_id", sa.Text(), nullable=False),
        sa.Column("principal_id", sa.Text(), nullable=False),
        sa.Column("doc_id", sa.Text(), nullable=False),
        sa.Column("action", sa.Text(), nullable=False),
        sa.Column("decision", sa.Text(), nullable=False),
        sa.Column("policy_version", sa.Text(), nullable=False),
        sa.Column("capability_version", sa.Text(), nullable=False),
        sa.Column("correlation_id", sa.Text(), nullable=False),
        sa.Column("occurred_at", sa.Text(), nullable=False),
        sa.CheckConstraint(
            "action = 'document.policy.update'",
            name="ck_document_access_admin_audit_action",
        ),
        sa.CheckConstraint(
            "decision = 'allowed'",
            name="ck_document_access_admin_audit_decision",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
            ondelete="NO ACTION",
        ),
        sa.PrimaryKeyConstraint("event_id"),
    )
    op.create_index(
        "ix_document_access_admin_audit_tenant_occurred",
        "document_access_admin_audit_events",
        ["tenant_id", "occurred_at"],
        unique=False,
    )

    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    op.execute("ALTER TABLE document_access_admin_audit_events ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE document_access_admin_audit_events FORCE ROW LEVEL SECURITY")
    op.execute(
        f"""
        CREATE POLICY {POLICY_NAME} ON document_access_admin_audit_events
        USING ({TENANT_EXPRESSION})
        WITH CHECK ({TENANT_EXPRESSION})
        """
    )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(f"DROP POLICY IF EXISTS {POLICY_NAME} ON document_access_admin_audit_events")
        op.execute("ALTER TABLE document_access_admin_audit_events NO FORCE ROW LEVEL SECURITY")
        op.execute("ALTER TABLE document_access_admin_audit_events DISABLE ROW LEVEL SECURITY")

    op.drop_table("document_access_admin_audit_events")
