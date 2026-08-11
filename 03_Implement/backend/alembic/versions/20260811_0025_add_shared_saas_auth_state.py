"""add shared SaaS tenant-session and JWT replay state

Revision ID: 20260811_0025
Revises: 20260811_0024
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260811_0025"
down_revision: str | None = "20260811_0024"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "saas_tenant_sessions",
        sa.Column("principal_id", sa.String(512), nullable=False),
        sa.Column("session_version", sa.String(128), nullable=False),
        sa.Column("updated_at", sa.String(40), nullable=False),
        sa.PrimaryKeyConstraint("principal_id"),
        sa.UniqueConstraint(
            "session_version", name="uq_saas_tenant_sessions_version"
        ),
    )
    op.create_table(
        "jwt_replay_tokens",
        sa.Column("token_digest", sa.String(64), nullable=False),
        sa.Column("expires_at", sa.String(40), nullable=False),
        sa.Column("recorded_at", sa.String(40), nullable=False),
        sa.PrimaryKeyConstraint("token_digest"),
    )
    op.create_index(
        "ix_jwt_replay_tokens_expires_at",
        "jwt_replay_tokens",
        ["expires_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_jwt_replay_tokens_expires_at", table_name="jwt_replay_tokens")
    op.drop_table("jwt_replay_tokens")
    op.drop_table("saas_tenant_sessions")
