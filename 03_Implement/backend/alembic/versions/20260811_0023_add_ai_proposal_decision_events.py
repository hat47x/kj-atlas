"""add tenant-scoped AI proposal decision audit events

Revision ID: 20260811_0023
Revises: 20260811_0022
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260811_0023"
down_revision: str | None = "20260811_0022"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_TABLE = "ai_proposal_decision_events"
_STATE_TABLE = "ai_proposal_decision_states"
_PROPOSAL_TABLE = "ai_proposals"
_POLICY = "kj_atlas_ai_proposal_decision_events_tenant_isolation"
_STATE_POLICY = "kj_atlas_ai_proposal_decision_states_tenant_isolation"
_PROPOSAL_POLICY = "kj_atlas_ai_proposals_tenant_isolation"
_TENANT_USING = "tenant_id = NULLIF(current_setting('kj_atlas.tenant_id', true), '')"


def upgrade() -> None:
    op.create_table(
        _PROPOSAL_TABLE,
        sa.Column("tenant_id", sa.String(128), nullable=False),
        sa.Column("doc_id", sa.String(128), nullable=False),
        sa.Column("proposal_id", sa.String(128), nullable=False),
        sa.Column("proposal_kind", sa.String(32), nullable=False),
        sa.Column("source_bundle_hash", sa.String(64), nullable=False),
        sa.Column("created_at", sa.String(40), nullable=False),
        sa.CheckConstraint(
            "length(source_bundle_hash) = 64",
            name="ck_ai_proposals_bundle_hash_length",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "doc_id"],
            ["documents.tenant_id", "documents.id"],
            name="fk_ai_proposals_tenant_document",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("tenant_id", "doc_id", "proposal_id"),
    )
    op.create_table(
        _STATE_TABLE,
        sa.Column("tenant_id", sa.String(128), nullable=False),
        sa.Column("doc_id", sa.String(128), nullable=False),
        sa.Column("proposal_id", sa.String(128), nullable=False),
        sa.Column("source_bundle_hash", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.String(40), nullable=False),
        sa.CheckConstraint(
            "status IN ('accepted', 'rejected', 'held')",
            name="ck_ai_proposal_decision_states_status",
        ),
        sa.CheckConstraint(
            "length(source_bundle_hash) = 64",
            name="ck_ai_proposal_decision_states_bundle_hash_length",
        ),
        sa.CheckConstraint("version >= 1", name="ck_ai_proposal_decision_states_version"),
        sa.ForeignKeyConstraint(
            ["tenant_id", "doc_id"],
            ["documents.tenant_id", "documents.id"],
            name="fk_ai_proposal_decision_states_tenant_document",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("tenant_id", "doc_id", "proposal_id"),
    )
    op.create_table(
        _TABLE,
        sa.Column("event_id", sa.String(128), nullable=False),
        sa.Column("tenant_id", sa.String(128), nullable=False),
        sa.Column("doc_id", sa.String(128), nullable=False),
        sa.Column("proposal_id", sa.String(128), nullable=False),
        sa.Column("source_bundle_hash", sa.String(64), nullable=False),
        sa.Column("idempotency_key", sa.String(512), nullable=False),
        sa.Column("decision", sa.String(32), nullable=False),
        sa.Column("reviewer_ref", sa.String(512), nullable=False),
        sa.Column("reason_sha256", sa.String(64), nullable=True),
        sa.Column("reason_utf8_bytes", sa.Integer(), nullable=False),
        sa.Column("recorded_at", sa.String(40), nullable=False),
        sa.CheckConstraint(
            "decision IN ('accepted', 'rejected', 'held')",
            name="ck_ai_proposal_decision_events_decision",
        ),
        sa.CheckConstraint(
            "length(source_bundle_hash) = 64",
            name="ck_ai_proposal_decision_events_bundle_hash_length",
        ),
        sa.CheckConstraint(
            "reason_utf8_bytes >= 0",
            name="ck_ai_proposal_decision_events_reason_size",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "doc_id"],
            ["documents.tenant_id", "documents.id"],
            name="fk_ai_proposal_decision_events_tenant_document",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("event_id"),
        sa.UniqueConstraint(
            "tenant_id",
            "doc_id",
            "idempotency_key",
            name="uq_ai_proposal_decision_events_idempotency",
        ),
    )
    op.create_index(
        "ix_ai_proposal_decision_events_proposal_order",
        _TABLE,
        ["tenant_id", "doc_id", "proposal_id", "recorded_at", "event_id"],
    )
    if op.get_bind().dialect.name == "postgresql":
        op.execute(sa.text(f"ALTER TABLE {_PROPOSAL_TABLE} ENABLE ROW LEVEL SECURITY"))
        op.execute(sa.text(f"ALTER TABLE {_PROPOSAL_TABLE} FORCE ROW LEVEL SECURITY"))
        op.execute(
            sa.text(
                f"CREATE POLICY {_PROPOSAL_POLICY} ON {_PROPOSAL_TABLE} "
                f"USING ({_TENANT_USING}) WITH CHECK ({_TENANT_USING})"
            )
        )
        op.execute(sa.text(f"ALTER TABLE {_STATE_TABLE} ENABLE ROW LEVEL SECURITY"))
        op.execute(sa.text(f"ALTER TABLE {_STATE_TABLE} FORCE ROW LEVEL SECURITY"))
        op.execute(
            sa.text(
                f"CREATE POLICY {_STATE_POLICY} ON {_STATE_TABLE} "
                f"USING ({_TENANT_USING}) WITH CHECK ({_TENANT_USING})"
            )
        )
        op.execute(sa.text(f"ALTER TABLE {_TABLE} ENABLE ROW LEVEL SECURITY"))
        op.execute(sa.text(f"ALTER TABLE {_TABLE} FORCE ROW LEVEL SECURITY"))
        op.execute(
            sa.text(
                f"CREATE POLICY {_POLICY} ON {_TABLE} "
                f"USING ({_TENANT_USING}) WITH CHECK ({_TENANT_USING})"
            )
        )


def downgrade() -> None:
    op.drop_table(_TABLE)
    op.drop_table(_STATE_TABLE)
    op.drop_table(_PROPOSAL_TABLE)
