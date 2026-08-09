"""add canvas revision retention pins

Revision ID: 20260810_0017
Revises: 20260809_0016
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260810_0017"
down_revision: str | None = "20260809_0016"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_TABLE = "canvas_revision_pins"
_POLICY = "kj_atlas_canvas_revision_pins_tenant_isolation"
_TENANT_USING = "tenant_id = NULLIF(current_setting('kj_atlas.tenant_id', true), '')"


def upgrade() -> None:
    op.create_table(
        _TABLE,
        sa.Column("tenant_id", sa.Text(), nullable=False),
        sa.Column("revision_id", sa.Text(), nullable=False),
        sa.Column("pin_reason", sa.Text(), nullable=False),
        sa.Column("created_at", sa.Text(), nullable=False),
        sa.CheckConstraint("length(trim(pin_reason)) > 0", name="ck_canvas_revision_pins_reason"),
        sa.ForeignKeyConstraint(
            ["tenant_id", "revision_id"],
            ["canvas_revisions.tenant_id", "canvas_revisions.revision_id"],
            name="fk_canvas_revision_pins_revision",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("tenant_id", "revision_id"),
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
    op.drop_table(_TABLE)
