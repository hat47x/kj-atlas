"""add server-owned guest auth sessions

Revision ID: 20260906_0034
Revises: 20260906_0033

The guest cookie is resolved before a tenant is known, so this authentication
state deliberately mirrors the pre-tenant nature of saas_auth_sessions rather
than enabling tenant RLS on the session table itself.  The row establishes only
(tenant, guest principal); authorization still returns to the FORCE-RLS guest
principal/grant/document tables on every request.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260906_0034"
down_revision: str | None = "20260906_0033"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "guest_auth_sessions",
        sa.Column("session_key_hash", sa.String(256), nullable=False),
        sa.Column("tenant_id", sa.String(128), nullable=False),
        sa.Column("guest_principal_id", sa.String(128), nullable=False),
        sa.Column("issuer", sa.String(512), nullable=False),
        sa.Column("subject", sa.String(512), nullable=False),
        sa.Column("created_at", sa.String(40), nullable=False),
        sa.Column("last_used_at", sa.String(40), nullable=False),
        sa.Column("absolute_expires_at", sa.String(40), nullable=False),
        sa.Column("revoked_at", sa.String(40), nullable=True),
        sa.PrimaryKeyConstraint("session_key_hash", name="pk_guest_auth_sessions"),
        sa.ForeignKeyConstraint(
            ["tenant_id", "guest_principal_id"],
            ["guest_principals.tenant_id", "guest_principals.guest_principal_id"],
            name="fk_guest_auth_sessions_principal",
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        "ix_guest_auth_sessions_principal",
        "guest_auth_sessions",
        ["tenant_id", "guest_principal_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_guest_auth_sessions_principal", table_name="guest_auth_sessions")
    op.drop_table("guest_auth_sessions")
