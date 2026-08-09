"""add privacy-minimal AI generation run lineage

Revision ID: 20260810_0018
Revises: 20260810_0017
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260810_0018"
down_revision: str | None = "20260810_0017"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_TABLE = "ai_generation_runs"
_POLICY = "kj_atlas_ai_generation_runs_tenant_isolation"
_TENANT_USING = "tenant_id = NULLIF(current_setting('kj_atlas.tenant_id', true), '')"


def upgrade() -> None:
    op.create_table(
        _TABLE,
        sa.Column("tenant_id", sa.Text(), nullable=False),
        sa.Column("ai_run_id", sa.Text(), nullable=False),
        sa.Column("task", sa.Text(), nullable=False),
        sa.Column("trace_id", sa.Text(), nullable=False),
        sa.Column("input_ir_digest", sa.Text(), nullable=False),
        sa.Column("output_digest", sa.Text(), nullable=False),
        sa.Column("policy_version", sa.Text(), nullable=False),
        sa.Column("safe_mode", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.Text(), nullable=False),
        sa.Column("retention_expires_at", sa.Text(), nullable=True),
        sa.CheckConstraint("length(trim(task)) > 0", name="ck_ai_generation_runs_task"),
        sa.CheckConstraint(
            "length(input_ir_digest) = 64", name="ck_ai_generation_runs_input_digest"
        ),
        sa.CheckConstraint(
            "length(output_digest) = 64", name="ck_ai_generation_runs_output_digest"
        ),
        sa.CheckConstraint("safe_mode IS TRUE", name="ck_ai_generation_runs_safe_mode"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="NO ACTION"),
        sa.ForeignKeyConstraint(
            ["tenant_id", "output_digest"],
            ["content_blobs.tenant_id", "content_blobs.content_digest"],
            name="fk_ai_generation_runs_output_blob",
            ondelete="NO ACTION",
        ),
        sa.PrimaryKeyConstraint("tenant_id", "ai_run_id"),
    )
    op.create_index("ix_ai_generation_runs_tenant_created", _TABLE, ["tenant_id", "created_at"])
    with op.batch_alter_table("canvas_revisions") as batch_op:
        batch_op.create_check_constraint(
            "ck_canvas_revisions_ai_proposal",
            "(generation_origin = 'ai_proposal' AND ai_run_ref IS NOT NULL) OR "
            "(generation_origin != 'ai_proposal' AND ai_run_ref IS NULL)",
        )
        batch_op.create_foreign_key(
            "fk_canvas_revisions_ai_run",
            _TABLE,
            ["tenant_id", "ai_run_ref"],
            ["tenant_id", "ai_run_id"],
            ondelete="NO ACTION",
        )
    if op.get_bind().dialect.name == "postgresql":
        op.execute(sa.text(f"ALTER TABLE {_TABLE} ENABLE ROW LEVEL SECURITY"))
        op.execute(sa.text(f"ALTER TABLE {_TABLE} FORCE ROW LEVEL SECURITY"))
        op.execute(
            sa.text(
                f"CREATE POLICY {_POLICY} ON {_TABLE} USING ({_TENANT_USING}) WITH CHECK ({_TENANT_USING})"
            )
        )


def downgrade() -> None:
    with op.batch_alter_table("canvas_revisions") as batch_op:
        batch_op.drop_constraint("fk_canvas_revisions_ai_run", type_="foreignkey")
        batch_op.drop_constraint("ck_canvas_revisions_ai_proposal", type_="check")
    if op.get_bind().dialect.name == "postgresql":
        op.execute(sa.text(f"DROP POLICY IF EXISTS {_POLICY} ON {_TABLE}"))
    op.drop_table(_TABLE)
