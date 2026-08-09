"""add canvas revision DAG and content blobs

Revision ID: 20260809_0016
Revises: 20260809_0015
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260809_0016"
down_revision: str | None = "20260809_0015"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_RLS_TABLES = (
    "content_blobs",
    "canvas_revisions",
    "canvas_revision_parents",
    "canvas_revision_heads",
)
_TENANT_USING = "tenant_id = NULLIF(current_setting('kj_atlas.tenant_id', true), '')"


def _policy_name(table_name: str) -> str:
    return f"kj_atlas_{table_name}_tenant_isolation"


def upgrade() -> None:
    op.create_table(
        "content_blobs",
        sa.Column("tenant_id", sa.Text(), nullable=False),
        sa.Column("content_digest", sa.Text(), nullable=False),
        sa.Column("storage_backend", sa.Text(), nullable=False),
        sa.Column("locator", sa.Text(), nullable=True),
        sa.Column("representation", sa.Text(), nullable=False),
        sa.Column("base_digest", sa.Text(), nullable=True),
        sa.Column("delta_depth", sa.Integer(), nullable=False),
        sa.Column("byte_size", sa.Integer(), nullable=False),
        sa.Column("stored_byte_size", sa.Integer(), nullable=False),
        sa.Column("storage_state", sa.Text(), nullable=False),
        sa.Column("schema_version", sa.Text(), nullable=False),
        sa.Column("created_at", sa.Text(), nullable=False),
        sa.CheckConstraint(
            "storage_backend IN ('database','nas','s3','git')", name="ck_content_blobs_backend"
        ),
        sa.CheckConstraint(
            "representation IN ('full_json','gzip_json','gzip_delta')",
            name="ck_content_blobs_representation",
        ),
        sa.CheckConstraint(
            "(representation = 'gzip_delta' AND base_digest IS NOT NULL AND delta_depth > 0) OR (representation != 'gzip_delta' AND base_digest IS NULL AND delta_depth = 0)",
            name="ck_content_blobs_delta_shape",
        ),
        sa.CheckConstraint(
            "storage_state IN ('pending','ready','deleting','failed')",
            name="ck_content_blobs_state",
        ),
        sa.CheckConstraint("byte_size >= 0", name="ck_content_blobs_byte_size"),
        sa.CheckConstraint("stored_byte_size >= 0", name="ck_content_blobs_stored_byte_size"),
        sa.CheckConstraint("length(content_digest) = 64", name="ck_content_blobs_digest_length"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["tenant_id", "base_digest"],
            ["content_blobs.tenant_id", "content_blobs.content_digest"],
            name="fk_content_blobs_base",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("tenant_id", "content_digest"),
    )
    op.create_index(
        "ix_content_blobs_tenant_state", "content_blobs", ["tenant_id", "storage_state"]
    )
    op.create_table(
        "canvas_revisions",
        sa.Column("tenant_id", sa.Text(), nullable=False),
        sa.Column("revision_id", sa.Text(), nullable=False),
        sa.Column("doc_id", sa.Text(), nullable=False),
        sa.Column("content_digest", sa.Text(), nullable=False),
        sa.Column("generation_tier", sa.Text(), nullable=False),
        sa.Column("generation_reason", sa.Text(), nullable=False),
        sa.Column("generation_origin", sa.Text(), nullable=False),
        sa.Column("actor_ref", sa.Text(), nullable=True),
        sa.Column("ai_run_ref", sa.Text(), nullable=True),
        sa.Column("source_revision_id", sa.Text(), nullable=True),
        sa.Column("created_at", sa.Text(), nullable=False),
        sa.CheckConstraint(
            "generation_tier IN ('ephemeral','checkpoint','governed')",
            name="ck_canvas_revisions_tier",
        ),
        sa.CheckConstraint(
            "generation_origin IN ('human','ai_proposal','system','import')",
            name="ck_canvas_revisions_origin",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "doc_id"],
            ["documents.tenant_id", "documents.id"],
            name="fk_canvas_revisions_document",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "content_digest"],
            ["content_blobs.tenant_id", "content_blobs.content_digest"],
            name="fk_canvas_revisions_blob",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "source_revision_id"],
            ["canvas_revisions.tenant_id", "canvas_revisions.revision_id"],
            name="fk_canvas_revisions_source",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("tenant_id", "revision_id"),
    )
    op.create_index(
        "ix_canvas_revisions_tenant_doc_created",
        "canvas_revisions",
        ["tenant_id", "doc_id", "created_at"],
    )
    op.create_table(
        "canvas_revision_parents",
        sa.Column("tenant_id", sa.Text(), nullable=False),
        sa.Column("revision_id", sa.Text(), nullable=False),
        sa.Column("parent_revision_id", sa.Text(), nullable=False),
        sa.Column("parent_order", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "revision_id != parent_revision_id", name="ck_canvas_revision_parents_not_self"
        ),
        sa.CheckConstraint("parent_order >= 0", name="ck_canvas_revision_parents_order"),
        sa.ForeignKeyConstraint(
            ["tenant_id", "revision_id"],
            ["canvas_revisions.tenant_id", "canvas_revisions.revision_id"],
            name="fk_canvas_revision_parents_revision",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "parent_revision_id"],
            ["canvas_revisions.tenant_id", "canvas_revisions.revision_id"],
            name="fk_canvas_revision_parents_parent",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("tenant_id", "revision_id", "parent_revision_id"),
        sa.UniqueConstraint(
            "tenant_id", "revision_id", "parent_order", name="uq_canvas_revision_parents_order"
        ),
    )
    op.create_table(
        "canvas_revision_heads",
        sa.Column("tenant_id", sa.Text(), nullable=False),
        sa.Column("doc_id", sa.Text(), nullable=False),
        sa.Column("head_name", sa.Text(), nullable=False),
        sa.Column("revision_id", sa.Text(), nullable=False),
        sa.Column("head_version", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.Text(), nullable=False),
        sa.CheckConstraint("length(trim(head_name)) > 0", name="ck_canvas_revision_heads_name"),
        sa.CheckConstraint("head_version > 0", name="ck_canvas_revision_heads_version"),
        sa.ForeignKeyConstraint(
            ["tenant_id", "doc_id"],
            ["documents.tenant_id", "documents.id"],
            name="fk_canvas_revision_heads_document",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "revision_id"],
            ["canvas_revisions.tenant_id", "canvas_revisions.revision_id"],
            name="fk_canvas_revision_heads_revision",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("tenant_id", "doc_id", "head_name"),
    )
    if op.get_bind().dialect.name == "postgresql":
        for table_name in _RLS_TABLES:
            op.execute(sa.text(f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY"))
            op.execute(sa.text(f"ALTER TABLE {table_name} FORCE ROW LEVEL SECURITY"))
            op.execute(
                sa.text(
                    f"CREATE POLICY {_policy_name(table_name)} ON {table_name} "
                    f"USING ({_TENANT_USING}) WITH CHECK ({_TENANT_USING})"
                )
            )


def downgrade() -> None:
    if op.get_bind().dialect.name == "postgresql":
        for table_name in reversed(_RLS_TABLES):
            op.execute(sa.text(f"DROP POLICY IF EXISTS {_policy_name(table_name)} ON {table_name}"))
    op.drop_table("canvas_revision_heads")
    op.drop_table("canvas_revision_parents")
    op.drop_table("canvas_revisions")
    op.drop_table("content_blobs")
