"""add inquiry bundle creator (SEC-INQUIRY-BOUND-01)

Revision ID: 20260822_0032
Revises: 20260815_0031

`inquiry_bundles` に `created_by` を足す（nullable、不変事実。ADR-0073の
documents.created_byと同じ設計: 既存bundleはNULL=「不明」のまま、遡って
バックフィルしない）。新規bundleにのみ作成者チェックを適用する方針
（issue-SEC-INQUIRY-BOUND-01、2026-08-22 Maintainer決定）に対応する列を
追加するだけで、既存bundleのアクセス可否は変えない。
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260822_0032"
down_revision: str | None = "20260815_0031"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("inquiry_bundles", sa.Column("created_by", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("inquiry_bundles", "created_by")
