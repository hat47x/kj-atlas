from __future__ import annotations

import os
import re
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, delete, select, text, update
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from kj_atlas_api.db import _normalize_database_url
from kj_atlas_api.models import (
    DocumentAccessAdminAuditEventRow,
    DocumentAccessMetadataRow,
    DocumentRow,
    MergeDecisionLogRow,
    TenantRow,
)
from kj_atlas_api.tenant_context import TenantContext
from kj_atlas_api.tenant_db_guard import apply_database_tenant_context


RUN_RLS_TESTS_ENV = "KJ_ATLAS_RUN_PG_RLS_TESTS"
ADMIN_DATABASE_URL_ENV = "KJ_ATLAS_DATABASE_URL"
RUNTIME_DATABASE_URL_ENV = "KJ_ATLAS_TEST_POSTGRES_RUNTIME_DATABASE_URL"
BACKEND_DIR = Path(__file__).resolve().parents[1]
RLS_PROTECTED_MODELS = (
    DocumentRow,
    MergeDecisionLogRow,
    DocumentAccessMetadataRow,
    DocumentAccessAdminAuditEventRow,
)


def test_postgres_rls_matrix_covers_every_migration_protected_table() -> None:
    enabled_tables: set[str] = set()
    write_checked_tables: set[str] = set()
    for migration_path in (BACKEND_DIR / "alembic" / "versions").glob("*.py"):
        migration_source = migration_path.read_text(encoding="utf-8")
        enabled_tables.update(
            re.findall(
                r"ALTER TABLE ([a-z0-9_]+) ENABLE ROW LEVEL SECURITY",
                migration_source,
            )
        )
        write_checked_tables.update(
            re.findall(
                r"CREATE POLICY [^\r\n]+ ON ([a-z0-9_]+)\s+"
                r"USING \([^\r\n]+\)\s+WITH CHECK \([^\r\n]+\)",
                migration_source,
            )
        )

    protected_model_tables = {model.__tablename__ for model in RLS_PROTECTED_MODELS}
    assert protected_model_tables == enabled_tables
    assert write_checked_tables == enabled_tables


def _tenant(tenant_id: str) -> TenantContext:
    return TenantContext(
        tenant_id=tenant_id,
        membership_id=f"membership-{tenant_id}",
        resolved_by="verified_claim",
    )


@pytest.fixture(scope="module")
def postgres_rls_engines() -> Iterator[tuple[Engine, Engine]]:
    if os.getenv(RUN_RLS_TESTS_ENV) != "1":
        pytest.skip(
            f"set {RUN_RLS_TESTS_ENV}=1 with separate admin/runtime PostgreSQL URLs",
            allow_module_level=False,
        )

    admin_url = os.getenv(ADMIN_DATABASE_URL_ENV, "")
    runtime_url = os.getenv(RUNTIME_DATABASE_URL_ENV, "")
    if not admin_url.startswith("postgresql") or not runtime_url.startswith("postgresql"):
        pytest.fail(
            f"{ADMIN_DATABASE_URL_ENV} and {RUNTIME_DATABASE_URL_ENV} must be PostgreSQL URLs"
        )
    if admin_url == runtime_url:
        pytest.fail("RLS verification requires distinct migration and runtime credentials")

    migration_env = os.environ.copy()
    migration_env[ADMIN_DATABASE_URL_ENV] = admin_url
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=BACKEND_DIR,
        env=migration_env,
        check=True,
    )

    admin_engine = create_engine(_normalize_database_url(admin_url))
    runtime_engine = create_engine(
        _normalize_database_url(runtime_url),
        pool_size=1,
        max_overflow=0,
    )
    try:
        with runtime_engine.connect() as connection:
            posture = connection.execute(
                text("SELECT rolsuper, rolbypassrls FROM pg_roles WHERE rolname = current_user")
            ).one()
            assert posture.rolsuper is False, "runtime role must not be a superuser"
            assert posture.rolbypassrls is False, "runtime role must not have BYPASSRLS"
            assert connection.execute(text("SHOW row_security")).scalar_one() == "on"
        yield admin_engine, runtime_engine
    finally:
        runtime_engine.dispose()
        admin_engine.dispose()


def _seed_tenant_documents(
    *,
    admin_engine: Engine,
    runtime_engine: Engine,
    tenant_ids: tuple[str, str],
    doc_ids: tuple[str, str],
) -> None:
    with Session(admin_engine) as db:
        for tenant_id in tenant_ids:
            db.add(
                TenantRow(
                    id=tenant_id,
                    display_name=tenant_id,
                    lifecycle_state="active",
                    created_at="2026-07-17T00:00:00Z",
                    updated_at="2026-07-17T00:00:00Z",
                )
            )
        db.commit()

    for index, (tenant_id, doc_id) in enumerate(zip(tenant_ids, doc_ids, strict=True)):
        with Session(runtime_engine) as db:
            apply_database_tenant_context(db=db, tenant=_tenant(tenant_id))
            db.add(
                DocumentRow(
                    tenant_id=tenant_id,
                    id=doc_id,
                    version=1,
                    updated_at="2026-07-17T00:00:00Z",
                    payload_json="{}",
                )
            )
            # Force the documents row to be physically inserted (and thus
            # visible to the FK check of the dependent rows below) before
            # they are added to the same flush. PostgreSQL FK checks bypass
            # RLS, but SQLAlchemy's automatic dependency sort across 3
            # sibling tables sharing the same (tenant_id, doc_id) composite
            # FK to `documents` is not reliable enough to trust implicitly.
            db.flush()
            db.add(
                DocumentAccessMetadataRow(
                    tenant_id=tenant_id,
                    doc_id=doc_id,
                    visibility="Public",
                    policy_binding_id=None,
                    policy_version=f"policy-v{index + 1}",
                    updated_at="2026-07-17T00:00:00Z",
                )
            )
            db.add(
                MergeDecisionLogRow(
                    tenant_id=tenant_id,
                    doc_id=doc_id,
                    decision_id=f"decision-{index + 1}",
                    group_id=f"group-{index + 1}",
                    snapshot_version=f"snapshot-v{index + 1}",
                    decided_at="2026-07-17T00:00:00Z",
                    payload_json="{}",
                )
            )
            db.add(
                DocumentAccessAdminAuditEventRow(
                    event_id=f"audit-{uuid4()}",
                    tenant_id=tenant_id,
                    principal_id=f"principal-{index + 1}",
                    doc_id=doc_id,
                    action="document.policy.update",
                    decision="allowed",
                    policy_version=f"policy-v{index + 1}",
                    capability_version="capability-v1",
                    correlation_id=f"correlation-{uuid4()}",
                    occurred_at="2026-07-17T00:00:00Z",
                )
            )
            db.commit()


def _cleanup(
    *,
    admin_engine: Engine,
    tenant_ids: tuple[str, str],
) -> None:
    for tenant_id in tenant_ids:
        with Session(admin_engine) as db:
            apply_database_tenant_context(db=db, tenant=_tenant(tenant_id))
            db.execute(
                delete(DocumentAccessAdminAuditEventRow).where(
                    DocumentAccessAdminAuditEventRow.tenant_id == tenant_id
                )
            )
            db.execute(
                delete(DocumentAccessMetadataRow).where(
                    DocumentAccessMetadataRow.tenant_id == tenant_id
                )
            )
            db.execute(
                delete(MergeDecisionLogRow).where(MergeDecisionLogRow.tenant_id == tenant_id)
            )
            db.execute(delete(DocumentRow).where(DocumentRow.tenant_id == tenant_id))
            db.commit()
    with Session(admin_engine) as db:
        db.execute(delete(TenantRow).where(TenantRow.id.in_(tenant_ids)))
        db.commit()


@pytest.mark.postgres
def test_all_rls_protected_document_tables_fail_closed_across_pool_reuse(
    postgres_rls_engines: tuple[Engine, Engine],
) -> None:
    admin_engine, runtime_engine = postgres_rls_engines
    suffix = uuid4().hex
    tenant_ids = (f"rls-a-{suffix}", f"rls-b-{suffix}")
    doc_ids = (f"doc-a-{suffix}", f"doc-b-{suffix}")

    _seed_tenant_documents(
        admin_engine=admin_engine,
        runtime_engine=runtime_engine,
        tenant_ids=tenant_ids,
        doc_ids=doc_ids,
    )
    try:
        with Session(runtime_engine) as db:
            apply_database_tenant_context(db=db, tenant=_tenant(tenant_ids[0]))
            documents = db.scalars(select(DocumentRow)).all()
            merge_decisions = db.scalars(select(MergeDecisionLogRow)).all()
            metadata = db.scalars(select(DocumentAccessMetadataRow)).all()
            audit_events = db.scalars(select(DocumentAccessAdminAuditEventRow)).all()
            assert [(row.tenant_id, row.id) for row in documents] == [(tenant_ids[0], doc_ids[0])]
            assert [(row.tenant_id, row.doc_id) for row in merge_decisions] == [
                (tenant_ids[0], doc_ids[0])
            ]
            assert [(row.tenant_id, row.doc_id) for row in metadata] == [
                (tenant_ids[0], doc_ids[0])
            ]
            assert [(row.tenant_id, row.doc_id) for row in audit_events] == [
                (tenant_ids[0], doc_ids[0])
            ]
            assert (
                db.scalars(select(DocumentRow).where(DocumentRow.tenant_id == tenant_ids[1])).all()
                == []
            )
            db.commit()

        # The pool has one connection. Transaction-local tenant state must not leak
        # into its next checkout when no context is applied.
        with Session(runtime_engine) as db:
            assert db.scalars(select(DocumentRow)).all() == []
            assert db.scalars(select(MergeDecisionLogRow)).all() == []
            assert db.scalars(select(DocumentAccessMetadataRow)).all() == []
            assert db.scalars(select(DocumentAccessAdminAuditEventRow)).all() == []

        with Session(runtime_engine) as db:
            apply_database_tenant_context(db=db, tenant=_tenant(tenant_ids[0]))
            document_update = db.execute(
                update(DocumentRow)
                .where(DocumentRow.tenant_id == tenant_ids[1])
                .values(payload_json='{"crossTenantWrite":true}')
            )
            merge_decision_update = db.execute(
                update(MergeDecisionLogRow)
                .where(MergeDecisionLogRow.tenant_id == tenant_ids[1])
                .values(group_id="cross-tenant-write")
            )
            metadata_update = db.execute(
                update(DocumentAccessMetadataRow)
                .where(DocumentAccessMetadataRow.tenant_id == tenant_ids[1])
                .values(
                    policy_version="cross-tenant-write",
                    updated_at="2026-07-17T00:00:01Z",
                )
            )
            audit_update = db.execute(
                update(DocumentAccessAdminAuditEventRow)
                .where(DocumentAccessAdminAuditEventRow.tenant_id == tenant_ids[1])
                .values(decision="cross-tenant-write")
            )
            assert document_update.rowcount == 0
            assert merge_decision_update.rowcount == 0
            assert metadata_update.rowcount == 0
            assert audit_update.rowcount == 0
            db.commit()

        reassignment_doc_id = f"reassign-{suffix}"
        with Session(runtime_engine) as db:
            apply_database_tenant_context(db=db, tenant=_tenant(tenant_ids[0]))
            db.add(
                DocumentRow(
                    tenant_id=tenant_ids[0],
                    id=reassignment_doc_id,
                    version=1,
                    updated_at="2026-07-17T00:00:00Z",
                    payload_json="{}",
                )
            )
            db.commit()

        with Session(runtime_engine) as db:
            apply_database_tenant_context(db=db, tenant=_tenant(tenant_ids[0]))
            with pytest.raises(SQLAlchemyError):
                db.execute(
                    update(DocumentRow)
                    .where(DocumentRow.id == reassignment_doc_id)
                    .values(tenant_id=tenant_ids[1])
                )
                db.commit()
            db.rollback()

        with Session(runtime_engine) as db:
            apply_database_tenant_context(db=db, tenant=_tenant(tenant_ids[0]))
            with pytest.raises(SQLAlchemyError):
                db.execute(
                    update(DocumentAccessAdminAuditEventRow)
                    .where(DocumentAccessAdminAuditEventRow.tenant_id == tenant_ids[0])
                    .values(tenant_id=tenant_ids[1])
                )
                db.commit()
            db.rollback()

        with Session(runtime_engine) as db:
            apply_database_tenant_context(db=db, tenant=_tenant(tenant_ids[0]))
            reassignment_document = db.scalar(
                select(DocumentRow).where(DocumentRow.id == reassignment_doc_id)
            )
            tenant_a_audit_events = db.scalars(select(DocumentAccessAdminAuditEventRow)).all()
            assert reassignment_document is not None
            assert reassignment_document.tenant_id == tenant_ids[0]
            assert tenant_a_audit_events
            assert all(row.tenant_id == tenant_ids[0] for row in tenant_a_audit_events)

        with Session(runtime_engine) as db:
            apply_database_tenant_context(db=db, tenant=_tenant(tenant_ids[1]))
            tenant_b_document = db.scalar(select(DocumentRow))
            tenant_b_merge_decision = db.scalar(select(MergeDecisionLogRow))
            tenant_b_metadata = db.scalar(select(DocumentAccessMetadataRow))
            tenant_b_audit_event = db.scalar(select(DocumentAccessAdminAuditEventRow))
            assert tenant_b_document is not None
            assert tenant_b_document.payload_json == "{}"
            assert tenant_b_merge_decision is not None
            assert tenant_b_merge_decision.group_id == "group-2"
            assert tenant_b_metadata is not None
            assert tenant_b_metadata.policy_version == "policy-v2"
            assert tenant_b_audit_event is not None
            assert tenant_b_audit_event.decision == "allowed"

        with Session(runtime_engine) as db:
            db.add(
                DocumentAccessAdminAuditEventRow(
                    event_id=f"audit-{uuid4()}",
                    tenant_id=tenant_ids[0],
                    principal_id="principal-missing-context",
                    doc_id=doc_ids[0],
                    action="document.policy.update",
                    decision="allowed",
                    policy_version="policy-v1",
                    capability_version="capability-v1",
                    correlation_id=f"correlation-{uuid4()}",
                    occurred_at="2026-07-17T00:00:01Z",
                )
            )
            with pytest.raises(SQLAlchemyError):
                db.commit()
            db.rollback()
    finally:
        _cleanup(admin_engine=admin_engine, tenant_ids=tenant_ids)
