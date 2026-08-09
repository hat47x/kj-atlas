"""add the single-tenant-compatible tenant foundation

Revision ID: 20260716_0006
Revises: 20260314_0005
Create Date: 2026-07-16 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260716_0006"
down_revision: str | None = "20260314_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

LOCAL_DEFAULT_TENANT_ID = "local-default"
MIGRATION_TIMESTAMP = "2026-07-16T00:00:00Z"


def _column_names(inspector: sa.Inspector, table_name: str) -> set[str]:
    return {column["name"] for column in inspector.get_columns(table_name)}


def _index_names(inspector: sa.Inspector, table_name: str) -> set[str]:
    return {index["name"] for index in inspector.get_indexes(table_name)}


def _ensure_local_default_tenant(bind: sa.Connection) -> None:
    existing = bind.execute(
        sa.text("SELECT 1 FROM tenants WHERE id = :tenant_id"),
        {"tenant_id": LOCAL_DEFAULT_TENANT_ID},
    ).first()
    if existing is not None:
        return

    bind.execute(
        sa.text(
            """
            INSERT INTO tenants (
                id, display_name, lifecycle_state, created_at, updated_at
            ) VALUES (
                :tenant_id, :display_name, 'active', :created_at, :updated_at
            )
            """
        ),
        {
            "tenant_id": LOCAL_DEFAULT_TENANT_ID,
            "display_name": "Local workspace",
            "created_at": MIGRATION_TIMESTAMP,
            "updated_at": MIGRATION_TIMESTAMP,
        },
    )


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("tenants"):
        op.create_table(
            "tenants",
            sa.Column("id", sa.Text(), nullable=False),
            sa.Column("display_name", sa.Text(), nullable=False),
            sa.Column("lifecycle_state", sa.Text(), nullable=False),
            sa.Column("created_at", sa.Text(), nullable=False),
            sa.Column("updated_at", sa.Text(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )

    if not inspector.has_table("identity_providers"):
        op.create_table(
            "identity_providers",
            sa.Column("id", sa.Text(), nullable=False),
            sa.Column("issuer", sa.Text(), nullable=False),
            sa.Column("audience", sa.Text(), nullable=False),
            sa.Column("lifecycle_state", sa.Text(), nullable=False),
            sa.Column("created_at", sa.Text(), nullable=False),
            sa.Column("updated_at", sa.Text(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "issuer",
                "audience",
                name="uq_identity_providers_issuer_audience",
            ),
        )

    if not inspector.has_table("tenant_identity_providers"):
        op.create_table(
            "tenant_identity_providers",
            sa.Column("tenant_id", sa.Text(), nullable=False),
            sa.Column("identity_provider_id", sa.Text(), nullable=False),
            sa.Column("lifecycle_state", sa.Text(), nullable=False),
            sa.Column("created_at", sa.Text(), nullable=False),
            sa.Column("updated_at", sa.Text(), nullable=False),
            sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(
                ["identity_provider_id"],
                ["identity_providers.id"],
                ondelete="CASCADE",
            ),
            sa.PrimaryKeyConstraint("tenant_id", "identity_provider_id"),
        )

    if not inspector.has_table("tenant_memberships"):
        op.create_table(
            "tenant_memberships",
            sa.Column("tenant_id", sa.Text(), nullable=False),
            sa.Column("user_id", sa.Text(), nullable=False),
            sa.Column("lifecycle_state", sa.Text(), nullable=False),
            sa.Column("created_at", sa.Text(), nullable=False),
            sa.Column("updated_at", sa.Text(), nullable=False),
            sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("tenant_id", "user_id"),
        )

    _ensure_local_default_tenant(bind)

    inspector = sa.inspect(bind)
    if inspector.has_table("documents"):
        if "tenant_id" not in _column_names(inspector, "documents"):
            op.add_column(
                "documents",
                sa.Column(
                    "tenant_id",
                    sa.Text(),
                    nullable=False,
                    server_default=LOCAL_DEFAULT_TENANT_ID,
                ),
            )
        inspector = sa.inspect(bind)
        if "ix_documents_tenant_id_id" not in _index_names(inspector, "documents"):
            op.create_index(
                "ix_documents_tenant_id_id",
                "documents",
                ["tenant_id", "id"],
                unique=True,
            )

    inspector = sa.inspect(bind)
    if inspector.has_table("merge_decision_logs"):
        if "tenant_id" not in _column_names(inspector, "merge_decision_logs"):
            op.add_column(
                "merge_decision_logs",
                sa.Column(
                    "tenant_id",
                    sa.Text(),
                    nullable=False,
                    server_default=LOCAL_DEFAULT_TENANT_ID,
                ),
            )
        inspector = sa.inspect(bind)
        merge_indexes = _index_names(inspector, "merge_decision_logs")
        if "ix_merge_decision_logs_tenant_doc_group_id" not in merge_indexes:
            op.create_index(
                "ix_merge_decision_logs_tenant_doc_group_id",
                "merge_decision_logs",
                ["tenant_id", "doc_id", "group_id", "id"],
                unique=False,
            )
        if "ix_merge_decision_logs_tenant_doc_snapshot_id" not in merge_indexes:
            op.create_index(
                "ix_merge_decision_logs_tenant_doc_snapshot_id",
                "merge_decision_logs",
                ["tenant_id", "doc_id", "snapshot_version", "id"],
                unique=False,
            )

    if inspector.has_table("users"):
        bind.execute(
            sa.text(
                """
                INSERT INTO tenant_memberships (
                    tenant_id, user_id, lifecycle_state, created_at, updated_at
                )
                SELECT :tenant_id, users.id, 'active', :created_at, :updated_at
                FROM users
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM tenant_memberships
                    WHERE tenant_memberships.tenant_id = :tenant_id
                      AND tenant_memberships.user_id = users.id
                )
                """
            ),
            {
                "tenant_id": LOCAL_DEFAULT_TENANT_ID,
                "created_at": MIGRATION_TIMESTAMP,
                "updated_at": MIGRATION_TIMESTAMP,
            },
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("merge_decision_logs"):
        merge_indexes = _index_names(inspector, "merge_decision_logs")
        if "ix_merge_decision_logs_tenant_doc_snapshot_id" in merge_indexes:
            op.drop_index(
                "ix_merge_decision_logs_tenant_doc_snapshot_id",
                table_name="merge_decision_logs",
            )
        if "ix_merge_decision_logs_tenant_doc_group_id" in merge_indexes:
            op.drop_index(
                "ix_merge_decision_logs_tenant_doc_group_id",
                table_name="merge_decision_logs",
            )
        if "tenant_id" in _column_names(sa.inspect(bind), "merge_decision_logs"):
            op.drop_column("merge_decision_logs", "tenant_id")

    inspector = sa.inspect(bind)
    if inspector.has_table("documents"):
        if "ix_documents_tenant_id_id" in _index_names(inspector, "documents"):
            op.drop_index("ix_documents_tenant_id_id", table_name="documents")
        if "tenant_id" in _column_names(sa.inspect(bind), "documents"):
            op.drop_column("documents", "tenant_id")

    # SAAS-TENANT-MIGRATION-01: data-safety guard — refuse to drop
    # tenant tables that contain rows beyond the local-default backfill.
    inspector = sa.inspect(bind)
    for table_name in (
        "tenant_memberships",
        "tenant_identity_providers",
        "identity_providers",
        "tenants",
    ):
        if inspector.has_table(table_name):
            if table_name == "tenants":
                count = bind.execute(
                    sa.text("SELECT COUNT(*) FROM tenants WHERE id != 'local-default'")
                ).scalar()
                if count:
                    raise RuntimeError(
                        f"Downgrade refused: {count} non-default tenant(s) "
                        "would be permanently deleted. Back up tenant data "
                        "before downgrading."
                    )
            elif table_name == "tenant_memberships":
                count = bind.execute(
                    sa.text(
                        "SELECT COUNT(*) FROM tenant_memberships "
                        "WHERE tenant_id != 'local-default'"
                    )
                ).scalar()
                if count:
                    raise RuntimeError(
                        f"Downgrade refused: {count} non-default "
                        "membership(s) would be permanently deleted."
                    )
            elif table_name == "identity_providers":
                count = bind.execute(
                    sa.text(
                        "SELECT COUNT(*) FROM identity_providers "
                        "WHERE id NOT LIKE 'idp-legacy-%'"
                    )
                ).scalar()
                if count:
                    raise RuntimeError(
                        f"Downgrade refused: {count} non-legacy identity "
                        "provider(s) would be permanently deleted."
                    )
            elif table_name == "tenant_identity_providers":
                count = bind.execute(
                    sa.text(
                        "SELECT COUNT(*) FROM tenant_identity_providers "
                        "WHERE tenant_id != 'local-default'"
                    )
                ).scalar()
                if count:
                    raise RuntimeError(
                        f"Downgrade refused: {count} non-default "
                        "tenant-IdP binding(s) would be permanently deleted."
                    )
            op.drop_table(table_name)
            inspector = sa.inspect(bind)
