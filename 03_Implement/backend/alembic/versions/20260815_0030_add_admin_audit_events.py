"""add control-plane admin audit trail (SEC-ADMIN-PLANE-03)

Revision ID: 20260815_0030
Revises: 20260815_0029

`admin_audit_events`：/admin/* 操作の監査証跡（主体フィンガープリント・route・
時刻・対象・結果）。fail-open 記録で操作を阻害しない。本文・secret・生PII・
policyRef生値は保存しない（ADR-0035）。
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260815_0030"
down_revision: str | None = "20260815_0029"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "admin_audit_events",
        sa.Column("event_id", sa.Text(), nullable=False),
        sa.Column("tenant_id", sa.Text(), nullable=True),
        sa.Column("actor_ref_hash", sa.Text(), nullable=True),
        sa.Column("route", sa.Text(), nullable=False),
        sa.Column("operation", sa.Text(), nullable=True),
        sa.Column("target", sa.Text(), nullable=True),
        sa.Column("result", sa.Text(), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=False),
        sa.Column("request_id", sa.Text(), nullable=True),
        sa.Column("occurred_at", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("event_id"),
    )
    op.create_index("ix_admin_audit_events_occurred", "admin_audit_events", ["occurred_at"])
    # MySQL/MariaDB key-length limit: composite index over two TEXT columns
    # exceeds 3072 bytes, so index route alone and filter by result in the row
    # set.
    op.create_index("ix_admin_audit_events_route", "admin_audit_events", ["route"])


def downgrade() -> None:
    op.drop_index("ix_admin_audit_events_route", table_name="admin_audit_events")
    op.drop_index("ix_admin_audit_events_occurred", table_name="admin_audit_events")
    op.drop_table("admin_audit_events")
