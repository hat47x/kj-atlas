"""enable PostgreSQL tenant row-level security

Revision ID: 20260717_0009
Revises: 20260717_0008
Create Date: 2026-07-17 04:00:00.000000
"""

from collections.abc import Sequence

from alembic import op

revision: str = "20260717_0009"
down_revision: str | None = "20260717_0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

DOCUMENT_POLICY = "kj_atlas_documents_tenant_isolation"
MERGE_LOG_POLICY = "kj_atlas_merge_logs_tenant_isolation"
TENANT_EXPRESSION = (
    "tenant_id = NULLIF(current_setting('kj_atlas.tenant_id', true), '')"
)


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    op.execute("ALTER TABLE documents ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE documents FORCE ROW LEVEL SECURITY")
    op.execute(
        f"""
        CREATE POLICY {DOCUMENT_POLICY} ON documents
        USING ({TENANT_EXPRESSION})
        WITH CHECK ({TENANT_EXPRESSION})
        """
    )

    op.execute("ALTER TABLE merge_decision_logs ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE merge_decision_logs FORCE ROW LEVEL SECURITY")
    op.execute(
        f"""
        CREATE POLICY {MERGE_LOG_POLICY} ON merge_decision_logs
        USING ({TENANT_EXPRESSION})
        WITH CHECK ({TENANT_EXPRESSION})
        """
    )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    op.execute(f"DROP POLICY IF EXISTS {MERGE_LOG_POLICY} ON merge_decision_logs")
    op.execute("ALTER TABLE merge_decision_logs NO FORCE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE merge_decision_logs DISABLE ROW LEVEL SECURITY")

    op.execute(f"DROP POLICY IF EXISTS {DOCUMENT_POLICY} ON documents")
    op.execute("ALTER TABLE documents NO FORCE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE documents DISABLE ROW LEVEL SECURITY")
