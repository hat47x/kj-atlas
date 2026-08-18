"""add server-owned revision to inquiry_bundles

Revision ID: 20260813_0026
Revises: 20260811_0025
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260813_0026"
down_revision: str | None = "20260811_0025"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # DATA-INQUIRY-CONCURRENCY-01 (案A): optimistic-concurrency revision.
    # Existing rows start at revision 1.
    op.add_column(
        "inquiry_bundles",
        sa.Column("revision", sa.Integer(), nullable=False, server_default="1"),
    )


def downgrade() -> None:
    # revision carries a server_default; on SQL Server the default constraint
    # must be dropped before the column (see 0014 pattern).
    op.drop_column("inquiry_bundles", "revision", mssql_drop_default=True)
