"""add server-owned saas_auth_sessions table (ADR-0074 expand step)

Revision ID: 20260813_0027
Revises: 20260813_0026

SAAS-TENANT-SESSION-BINDING-01: expand-only. Adds the login-session-keyed
table ADR-0074 decision 3 specifies, alongside the existing principal-keyed
saas_tenant_sessions. Nothing reads or writes this table yet -- application
wiring (BFF cookie issuance, CAS active-tenant updates, cutover) is later
work. This migration can be reverted with no data-loss risk since no
consumer exists.

Originally chained after 20260813_0026 (another session's in-progress
inquiry_bundles.revision migration, on their local ci/upgrade-actions-node24
branch). That branch was never merged into main via origin, so 20260813_0026
does not exist here; re-chained onto 20260811_0025, the actual current tip.
Whoever merges that branch later will need to renumber one side to keep a
single head, same as any other two-migrations-added-concurrently case.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260813_0027"
down_revision: str | None = "20260813_0026"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "saas_auth_sessions",
        sa.Column("session_key_hash", sa.Text(), nullable=False),
        sa.Column("principal_id", sa.Text(), nullable=False),
        sa.Column("issuer", sa.Text(), nullable=False),
        sa.Column("subject", sa.Text(), nullable=False),
        sa.Column("active_tenant_id", sa.Text(), nullable=True),
        sa.Column("tenant_session_version", sa.Text(), nullable=False),
        sa.Column("created_at", sa.Text(), nullable=False),
        sa.Column("last_used_at", sa.Text(), nullable=False),
        sa.Column("absolute_expires_at", sa.Text(), nullable=False),
        sa.Column("revoked_at", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["active_tenant_id"],
            ["tenants.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("session_key_hash"),
    )
    op.create_index(
        "ix_saas_auth_sessions_principal_id",
        "saas_auth_sessions",
        ["principal_id"],
        unique=False,
    )
    op.create_index(
        "ix_saas_auth_sessions_issuer_subject",
        "saas_auth_sessions",
        ["issuer", "subject"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_saas_auth_sessions_issuer_subject", table_name="saas_auth_sessions")
    op.drop_index("ix_saas_auth_sessions_principal_id", table_name="saas_auth_sessions")
    op.drop_table("saas_auth_sessions")
