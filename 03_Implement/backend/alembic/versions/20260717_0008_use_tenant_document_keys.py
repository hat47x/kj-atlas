"""use tenant-scoped document keys

Revision ID: 20260717_0008
Revises: 20260717_0007
Create Date: 2026-07-17 02:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

from kj_atlas_api.database_support import database_support_for_backend

revision: str = "20260717_0008"
down_revision: str | None = "20260717_0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

OLD_DOCUMENT_INDEX = "ix_documents_tenant_id_id"
OLD_LOG_UNIQUE = "uq_merge_decision_logs_doc_decision"
NEW_DOCUMENT_PK = "pk_documents_tenant_id_id"
NEW_DOCUMENT_TENANT_FK = "fk_documents_tenant_id"
NEW_LOG_DOCUMENT_FK = "fk_merge_decision_logs_tenant_document"
NEW_LOG_UNIQUE = "uq_merge_decision_logs_tenant_doc_decision"


def _assert_existing_rows_are_consistent(bind: sa.Connection) -> None:
    documents = sa.table("documents", sa.column("id"), sa.column("tenant_id"))
    tenants = sa.table("tenants", sa.column("id"))
    logs = sa.table("merge_decision_logs", sa.column("doc_id"), sa.column("tenant_id"))
    orphan_document = bind.execute(
        sa.select(sa.literal(1))
        .select_from(documents.outerjoin(tenants, tenants.c.id == documents.c.tenant_id))
        .where(tenants.c.id.is_(None))
        .limit(1)
    ).first()
    if orphan_document is not None:
        raise RuntimeError("documents contains tenant_id values that do not exist in tenants")

    mismatched_log = bind.execute(
        sa.select(sa.literal(1))
        .select_from(
            logs.outerjoin(
                documents,
                sa.and_(
                    documents.c.tenant_id == logs.c.tenant_id,
                    documents.c.id == logs.c.doc_id,
                ),
            )
        )
        .where(documents.c.id.is_(None))
        .limit(1)
    ).first()
    if mismatched_log is not None:
        raise RuntimeError("merge_decision_logs contains tenant/document mismatches")


def _assert_global_document_ids_are_restorable(bind: sa.Connection) -> None:
    documents = sa.table("documents", sa.column("id"))
    duplicate = bind.execute(
        sa.select(documents.c.id).group_by(documents.c.id).having(sa.func.count() > 1).limit(1)
    ).first()
    if duplicate is not None:
        raise RuntimeError(
            "Cannot downgrade tenant-scoped document keys while duplicate docId values exist"
        )


def _sqlite_create_indexes(bind: sa.Connection, *, tenant_key: bool) -> None:
    if not tenant_key:
        bind.execute(
            sa.text(
                """
                CREATE UNIQUE INDEX ix_documents_tenant_id_id
                ON documents (tenant_id, id)
                """
            )
        )
    bind.execute(
        sa.text(
            """
            CREATE INDEX ix_merge_decision_logs_doc_group_id
            ON merge_decision_logs (doc_id, group_id, id)
            """
        )
    )
    bind.execute(
        sa.text(
            """
            CREATE INDEX ix_merge_decision_logs_doc_snapshot_id
            ON merge_decision_logs (doc_id, snapshot_version, id)
            """
        )
    )
    bind.execute(
        sa.text(
            """
            CREATE INDEX ix_merge_decision_logs_tenant_doc_group_id
            ON merge_decision_logs (tenant_id, doc_id, group_id, id)
            """
        )
    )
    bind.execute(
        sa.text(
            """
            CREATE INDEX ix_merge_decision_logs_tenant_doc_snapshot_id
            ON merge_decision_logs (tenant_id, doc_id, snapshot_version, id)
            """
        )
    )


def _sqlite_upgrade(bind: sa.Connection) -> None:
    bind.execute(
        sa.text(
            """
            CREATE TABLE documents__tenant_key (
                tenant_id TEXT NOT NULL DEFAULT 'local-default',
                id TEXT NOT NULL,
                version INTEGER NOT NULL,
                updated_at TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                CONSTRAINT pk_documents_tenant_id_id PRIMARY KEY (tenant_id, id),
                CONSTRAINT fk_documents_tenant_id
                    FOREIGN KEY (tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT
            )
            """
        )
    )
    bind.execute(
        sa.text(
            """
            INSERT INTO documents__tenant_key (
                tenant_id, id, version, updated_at, payload_json
            )
            SELECT tenant_id, id, version, updated_at, payload_json
            FROM documents
            """
        )
    )
    bind.execute(
        sa.text(
            """
            CREATE TABLE merge_decision_logs__tenant_key (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                tenant_id TEXT NOT NULL DEFAULT 'local-default',
                doc_id TEXT NOT NULL,
                decision_id TEXT NOT NULL,
                group_id TEXT NOT NULL,
                snapshot_version TEXT NOT NULL,
                decided_at TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                CONSTRAINT uq_merge_decision_logs_tenant_doc_decision
                    UNIQUE (tenant_id, doc_id, decision_id),
                CONSTRAINT fk_merge_decision_logs_tenant_document
                    FOREIGN KEY (tenant_id, doc_id)
                    REFERENCES documents__tenant_key (tenant_id, id)
                    ON DELETE CASCADE
            )
            """
        )
    )
    bind.execute(
        sa.text(
            """
            INSERT INTO merge_decision_logs__tenant_key (
                id, tenant_id, doc_id, decision_id, group_id,
                snapshot_version, decided_at, payload_json
            )
            SELECT id, tenant_id, doc_id, decision_id, group_id,
                   snapshot_version, decided_at, payload_json
            FROM merge_decision_logs
            """
        )
    )
    bind.execute(sa.text("DROP TABLE merge_decision_logs"))
    bind.execute(sa.text("DROP TABLE documents"))
    bind.execute(sa.text("ALTER TABLE documents__tenant_key RENAME TO documents"))
    bind.execute(
        sa.text("ALTER TABLE merge_decision_logs__tenant_key RENAME TO merge_decision_logs")
    )
    _sqlite_create_indexes(bind, tenant_key=True)


def _sqlite_downgrade(bind: sa.Connection) -> None:
    bind.execute(
        sa.text(
            """
            CREATE TABLE documents__global_key (
                id TEXT NOT NULL PRIMARY KEY,
                tenant_id TEXT NOT NULL DEFAULT 'local-default',
                version INTEGER NOT NULL,
                updated_at TEXT NOT NULL,
                payload_json TEXT NOT NULL
            )
            """
        )
    )
    bind.execute(
        sa.text(
            """
            INSERT INTO documents__global_key (
                id, tenant_id, version, updated_at, payload_json
            )
            SELECT id, tenant_id, version, updated_at, payload_json
            FROM documents
            """
        )
    )
    bind.execute(
        sa.text(
            """
            CREATE TABLE merge_decision_logs__global_key (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                tenant_id TEXT NOT NULL DEFAULT 'local-default',
                doc_id TEXT NOT NULL,
                decision_id TEXT NOT NULL,
                group_id TEXT NOT NULL,
                snapshot_version TEXT NOT NULL,
                decided_at TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                CONSTRAINT uq_merge_decision_logs_doc_decision
                    UNIQUE (doc_id, decision_id),
                FOREIGN KEY (doc_id) REFERENCES documents__global_key (id)
                    ON DELETE CASCADE
            )
            """
        )
    )
    bind.execute(
        sa.text(
            """
            INSERT INTO merge_decision_logs__global_key (
                id, tenant_id, doc_id, decision_id, group_id,
                snapshot_version, decided_at, payload_json
            )
            SELECT id, tenant_id, doc_id, decision_id, group_id,
                   snapshot_version, decided_at, payload_json
            FROM merge_decision_logs
            """
        )
    )
    bind.execute(sa.text("DROP TABLE merge_decision_logs"))
    bind.execute(sa.text("DROP TABLE documents"))
    bind.execute(sa.text("ALTER TABLE documents__global_key RENAME TO documents"))
    bind.execute(
        sa.text("ALTER TABLE merge_decision_logs__global_key RENAME TO merge_decision_logs")
    )
    _sqlite_create_indexes(bind, tenant_key=False)


def _named_primary_key(inspector: sa.Inspector) -> str:
    primary_key_name = inspector.get_pk_constraint("documents").get("name")
    if not primary_key_name and inspector.bind.dialect.name in {"mysql", "mariadb"}:
        return "PRIMARY"
    if not isinstance(primary_key_name, str) or not primary_key_name:
        raise RuntimeError("documents primary key must be named for constraint-DDL migration")
    return primary_key_name


def _matching_foreign_key_names(
    inspector: sa.Inspector,
    *,
    table_name: str,
    constrained_columns: list[str],
) -> list[str]:
    names: list[str] = []
    for foreign_key in inspector.get_foreign_keys(table_name):
        if foreign_key.get("constrained_columns") != constrained_columns:
            continue
        name = foreign_key.get("name")
        if not isinstance(name, str) or not name:
            raise RuntimeError(f"{table_name} foreign key must be named")
        names.append(name)
    return names


def _constraint_ddl_upgrade(bind: sa.Connection) -> None:
    inspector = sa.inspect(bind)
    for name in _matching_foreign_key_names(
        inspector,
        table_name="merge_decision_logs",
        constrained_columns=["doc_id"],
    ):
        op.drop_constraint(name, "merge_decision_logs", type_="foreignkey")
    op.drop_constraint(OLD_LOG_UNIQUE, "merge_decision_logs", type_="unique")
    op.drop_index(OLD_DOCUMENT_INDEX, table_name="documents")
    op.drop_constraint(_named_primary_key(sa.inspect(bind)), "documents", type_="primary")
    op.create_primary_key(NEW_DOCUMENT_PK, "documents", ["tenant_id", "id"])
    op.create_foreign_key(
        NEW_DOCUMENT_TENANT_FK,
        "documents",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete="NO ACTION",
    )
    op.create_foreign_key(
        NEW_LOG_DOCUMENT_FK,
        "merge_decision_logs",
        "documents",
        ["tenant_id", "doc_id"],
        ["tenant_id", "id"],
        ondelete="CASCADE",
    )
    op.create_unique_constraint(
        NEW_LOG_UNIQUE,
        "merge_decision_logs",
        ["tenant_id", "doc_id", "decision_id"],
    )


def _constraint_ddl_downgrade(bind: sa.Connection) -> None:
    op.drop_constraint(NEW_LOG_DOCUMENT_FK, "merge_decision_logs", type_="foreignkey")
    op.drop_constraint(NEW_LOG_UNIQUE, "merge_decision_logs", type_="unique")
    op.drop_constraint(NEW_DOCUMENT_TENANT_FK, "documents", type_="foreignkey")
    op.drop_constraint(_named_primary_key(sa.inspect(bind)), "documents", type_="primary")
    op.create_primary_key("pk_documents_id", "documents", ["id"])
    op.create_foreign_key(
        "fk_merge_decision_logs_doc_id",
        "merge_decision_logs",
        "documents",
        ["doc_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_unique_constraint(
        OLD_LOG_UNIQUE,
        "merge_decision_logs",
        ["doc_id", "decision_id"],
    )
    op.create_index(
        OLD_DOCUMENT_INDEX,
        "documents",
        ["tenant_id", "id"],
        unique=True,
    )


def upgrade() -> None:
    bind = op.get_bind()
    _assert_existing_rows_are_consistent(bind)
    strategy = database_support_for_backend(bind.dialect.name).migration_strategy
    if strategy == "sqlite-rebuild":
        _sqlite_upgrade(bind)
        return
    if strategy == "constraint-ddl":
        _constraint_ddl_upgrade(bind)
        return
    raise RuntimeError(f"Unsupported database dialect: {bind.dialect.name}")


def downgrade() -> None:
    bind = op.get_bind()
    _assert_global_document_ids_are_restorable(bind)
    strategy = database_support_for_backend(bind.dialect.name).migration_strategy
    if strategy == "sqlite-rebuild":
        _sqlite_downgrade(bind)
        return
    if strategy == "constraint-ddl":
        _constraint_ddl_downgrade(bind)
        return
    raise RuntimeError(f"Unsupported database dialect: {bind.dialect.name}")
