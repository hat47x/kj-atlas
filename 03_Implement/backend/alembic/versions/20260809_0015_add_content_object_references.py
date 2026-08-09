"""add content object reference metadata

Revision ID: 20260809_0015
Revises: 20260807_0014
Create Date: 2026-08-09 00:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260809_0015"
down_revision: str | None = "20260807_0014"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_TABLE = "content_object_references"
_POLICY = "kj_atlas_content_object_references_tenant_isolation"
_TENANT_USING = "tenant_id = NULLIF(current_setting('kj_atlas.tenant_id', true), '')"


def upgrade() -> None:
    op.create_table(
        _TABLE,
        sa.Column("content_id", sa.Text(), nullable=False),
        sa.Column("tenant_id", sa.Text(), nullable=False),
        sa.Column("storage_backend", sa.Text(), nullable=False),
        sa.Column("locator", sa.Text(), nullable=True),
        sa.Column("storage_state", sa.Text(), nullable=False),
        sa.Column("byte_size", sa.Integer(), nullable=False),
        sa.Column("sha256_digest", sa.Text(), nullable=False),
        sa.Column("schema_version", sa.Text(), nullable=False),
        sa.Column("created_at", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.Text(), nullable=False),
        sa.CheckConstraint(
            "storage_backend IN ('database', 'nas', 's3')",
            name="ck_content_object_references_backend",
        ),
        sa.CheckConstraint(
            "storage_state IN ('pending', 'ready', 'deleting', 'failed')",
            name="ck_content_object_references_state",
        ),
        sa.CheckConstraint(
            "(storage_backend = 'database' AND locator IS NULL) OR "
            "(storage_backend IN ('nas', 's3') AND locator IS NOT NULL "
            "AND length(trim(locator)) > 0)",
            name="ck_content_object_references_locator",
        ),
        sa.CheckConstraint("byte_size >= 0", name="ck_content_object_references_byte_size"),
        sa.CheckConstraint(
            "length(sha256_digest) = 64",
            name="ck_content_object_references_digest_length",
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="NO ACTION"),
        sa.PrimaryKeyConstraint("content_id"),
    )
    op.create_index(
        "ix_content_object_references_tenant_state",
        _TABLE,
        ["tenant_id", "storage_state"],
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
