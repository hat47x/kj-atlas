"""add one-time guest invitation redeem state

Revision ID: 20260907_0035
Revises: 20260906_0034

The opaque state is resolved before a tenant is known, so this table is
intentionally pre-tenant authentication state and is not protected by tenant
RLS. It grants no document access and only binds a short-lived handle to an
existing pending guest principal; tenant-scoped work resumes immediately after
state resolution.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260907_0035"
down_revision: str | None = "20260906_0034"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "guest_redeem_states",
        sa.Column("state_key_hash", sa.String(256), nullable=False),
        sa.Column("tenant_id", sa.String(128), nullable=False),
        sa.Column("guest_principal_id", sa.String(128), nullable=False),
        sa.Column("created_at", sa.String(40), nullable=False),
        sa.Column("expires_at", sa.String(40), nullable=False),
        sa.Column("consumed_at", sa.String(40), nullable=True),
        sa.PrimaryKeyConstraint("state_key_hash", name="pk_guest_redeem_states"),
        sa.ForeignKeyConstraint(
            ["tenant_id", "guest_principal_id"],
            ["guest_principals.tenant_id", "guest_principals.guest_principal_id"],
            name="fk_guest_redeem_states_principal",
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        "ix_guest_redeem_states_principal",
        "guest_redeem_states",
        ["tenant_id", "guest_principal_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_guest_redeem_states_principal", table_name="guest_redeem_states")
    op.drop_table("guest_redeem_states")
