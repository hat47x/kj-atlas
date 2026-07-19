"""add tenant-document foreign key to document access admin audit

Revision ID: 20260720_0012
Revises: 20260717_0011
Create Date: 2026-07-20 00:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.engine import Connection

revision: str = "20260720_0012"
down_revision: str | None = "20260717_0011"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TABLE_NAME = "document_access_admin_audit_events"
CONSTRAINT_NAME = "fk_document_access_admin_audit_tenant_document"


def _assert_no_orphaned_audit_events(bind: Connection) -> None:
    orphan = bind.execute(
        sa.text(
            """
            SELECT audit.event_id, audit.tenant_id, audit.doc_id
            FROM document_access_admin_audit_events AS audit
            LEFT JOIN documents AS document
              ON document.tenant_id = audit.tenant_id
             AND document.id = audit.doc_id
            WHERE document.id IS NULL
            LIMIT 1
            """
        )
    ).first()
    if orphan is not None:
        raise RuntimeError(
            "cannot add admin audit tenant-document foreign key: "
            "orphaned or cross-tenant audit event exists"
        )


def upgrade() -> None:
    bind = op.get_bind()
    _assert_no_orphaned_audit_events(bind)
    if bind.dialect.name == "sqlite":
        with op.batch_alter_table(TABLE_NAME, recreate="always") as batch_op:
            batch_op.create_foreign_key(
                CONSTRAINT_NAME,
                "documents",
                ["tenant_id", "doc_id"],
                ["tenant_id", "id"],
                ondelete="RESTRICT",
            )
        return

    op.create_foreign_key(
        CONSTRAINT_NAME,
        TABLE_NAME,
        "documents",
        ["tenant_id", "doc_id"],
        ["tenant_id", "id"],
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        with op.batch_alter_table(TABLE_NAME, recreate="always") as batch_op:
            batch_op.drop_constraint(CONSTRAINT_NAME, type_="foreignkey")
        return

    op.drop_constraint(CONSTRAINT_NAME, TABLE_NAME, type_="foreignkey")
