"""add external proposal provenance to the shared proposal audit ledger

Revision ID: 20260811_0024
Revises: 20260811_0023
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260811_0024"
down_revision: str | None = "20260811_0023"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    length_fn = "len" if op.get_bind().dialect.name == "mssql" else "length"
    op.create_table(
        "external_agent_tasks",
        sa.Column("tenant_id", sa.String(128), nullable=False),
        sa.Column("task_id", sa.String(128), nullable=False),
        sa.Column("doc_id", sa.String(128), nullable=False),
        sa.Column("base_doc_signature", sa.String(512), nullable=False),
        sa.Column("source_bundle_hash", sa.String(64), nullable=False),
        sa.Column("query_canonical_hash", sa.String(64), nullable=False),
        sa.Column("task_kind", sa.String(32), nullable=False),
        sa.Column("provenance_level", sa.String(32), nullable=False),
        sa.Column("created_at", sa.String(40), nullable=False),
        sa.CheckConstraint(
            f"{length_fn}(source_bundle_hash) = 64 AND "
            f"{length_fn}(query_canonical_hash) = 64",
            name="ck_external_agent_tasks_hash_lengths",
        ),
        sa.CheckConstraint(
            "provenance_level = 'user_presented_unsigned'",
            name="ck_external_agent_tasks_provenance",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "doc_id"],
            ["documents.tenant_id", "documents.id"],
            name="fk_external_agent_tasks_tenant_document",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("tenant_id", "task_id"),
    )
    if op.get_bind().dialect.name == "postgresql":
        tenant_using = "tenant_id = NULLIF(current_setting('kj_atlas.tenant_id', true), '')"
        op.execute(sa.text("ALTER TABLE external_agent_tasks ENABLE ROW LEVEL SECURITY"))
        op.execute(sa.text("ALTER TABLE external_agent_tasks FORCE ROW LEVEL SECURITY"))
        op.execute(
            sa.text(
                "CREATE POLICY kj_atlas_external_agent_tasks_tenant_isolation "
                "ON external_agent_tasks "
                f"USING ({tenant_using}) WITH CHECK ({tenant_using})"
            )
        )
    with op.batch_alter_table("ai_proposals") as batch:
        batch.add_column(sa.Column("origin", sa.String(32), nullable=False, server_default="internal"))
        batch.add_column(sa.Column("task_id", sa.String(128), nullable=True))
        batch.add_column(sa.Column("base_doc_signature", sa.String(512), nullable=True))
        batch.add_column(sa.Column("query_canonical_hash", sa.String(64), nullable=True))
        batch.add_column(sa.Column("proposal_fingerprint", sa.String(64), nullable=True))
        batch.add_column(sa.Column("provenance_level", sa.String(32), nullable=True))
        batch.create_check_constraint(
            "ck_ai_proposals_origin", "origin IN ('internal', 'external_agent')"
        )
        batch.create_check_constraint(
            "ck_ai_proposals_external_provenance",
            "(origin = 'internal' AND task_id IS NULL AND base_doc_signature IS NULL "
            "AND query_canonical_hash IS NULL AND proposal_fingerprint IS NULL "
            "AND provenance_level IS NULL) OR "
            "(origin = 'external_agent' AND task_id IS NOT NULL "
            f"AND base_doc_signature IS NOT NULL AND {length_fn}(query_canonical_hash) = 64 "
            f"AND {length_fn}(proposal_fingerprint) = 64 "
            "AND provenance_level = 'user_presented_unsigned')",
        )
    with op.batch_alter_table("ai_proposal_decision_events") as batch:
        batch.add_column(
            sa.Column("proposal_origin", sa.String(32), nullable=False, server_default="internal")
        )
        batch.add_column(sa.Column("provenance_level", sa.String(32), nullable=True))
        batch.create_check_constraint(
            "ck_ai_proposal_decision_events_origin",
            "proposal_origin IN ('internal', 'external_agent')",
        )
        batch.create_check_constraint(
            "ck_ai_proposal_decision_events_provenance",
            "(proposal_origin = 'internal' AND provenance_level IS NULL) OR "
            "(proposal_origin = 'external_agent' "
            "AND provenance_level = 'user_presented_unsigned')",
        )


def downgrade() -> None:
    with op.batch_alter_table("ai_proposal_decision_events") as batch:
        batch.drop_constraint("ck_ai_proposal_decision_events_provenance", type_="check")
        batch.drop_constraint("ck_ai_proposal_decision_events_origin", type_="check")
        batch.drop_column("provenance_level")
        batch.drop_column("proposal_origin", mssql_drop_default=True)
    with op.batch_alter_table("ai_proposals") as batch:
        batch.drop_constraint("ck_ai_proposals_external_provenance", type_="check")
        batch.drop_constraint("ck_ai_proposals_origin", type_="check")
        batch.drop_column("provenance_level")
        batch.drop_column("proposal_fingerprint")
        batch.drop_column("query_canonical_hash")
        batch.drop_column("base_doc_signature")
        batch.drop_column("task_id")
        batch.drop_column("origin", mssql_drop_default=True)
    op.drop_table("external_agent_tasks")
