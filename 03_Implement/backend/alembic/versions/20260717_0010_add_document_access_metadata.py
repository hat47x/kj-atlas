"""add tenant-scoped document access metadata

Revision ID: 20260717_0010
Revises: 20260717_0009
Create Date: 2026-07-17 08:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260717_0010"
down_revision: str | None = "20260717_0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

POLICY_NAME = "kj_atlas_document_access_metadata_tenant_isolation"
TENANT_EXPRESSION = (
    "tenant_id = NULLIF(current_setting('kj_atlas.tenant_id', true), '')"
)


def upgrade() -> None:
    op.create_table(
        "document_access_metadata",
        sa.Column("tenant_id", sa.Text(), nullable=False),
        sa.Column("doc_id", sa.Text(), nullable=False),
        sa.Column("visibility", sa.Text(), nullable=False),
        sa.Column("policy_binding_id", sa.Text(), nullable=True),
        sa.Column("policy_version", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.Text(), nullable=False),
        sa.CheckConstraint(
            "visibility IN ('Public', 'Unlisted', 'Org', 'Restricted')",
            name="ck_document_access_metadata_visibility",
        ),
        sa.CheckConstraint(
            "visibility IN ('Public', 'Unlisted') "
            "OR (policy_binding_id IS NOT NULL AND length(trim(policy_binding_id)) > 0)",
            name="ck_document_access_metadata_policy_binding",
        ),
        sa.CheckConstraint(
            "length(trim(policy_version)) > 0",
            name="ck_document_access_metadata_policy_version",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "doc_id"],
            ["documents.tenant_id", "documents.id"],
            name="fk_document_access_metadata_tenant_document",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("tenant_id", "doc_id"),
    )

    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    op.execute("ALTER TABLE document_access_metadata ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE document_access_metadata FORCE ROW LEVEL SECURITY")
    op.execute(
        f"""
        CREATE POLICY {POLICY_NAME} ON document_access_metadata
        USING ({TENANT_EXPRESSION})
        WITH CHECK ({TENANT_EXPRESSION})
        """
    )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(f"DROP POLICY IF EXISTS {POLICY_NAME} ON document_access_metadata")
        op.execute("ALTER TABLE document_access_metadata NO FORCE ROW LEVEL SECURITY")
        op.execute("ALTER TABLE document_access_metadata DISABLE ROW LEVEL SECURITY")

    op.drop_table("document_access_metadata")
