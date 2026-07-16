from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from kj_atlas_api.document_repository import (
    get_document_row,
    list_document_rows,
    list_merge_decision_logs_by_group,
    list_merge_decision_logs_by_snapshot,
)
from kj_atlas_api.models import Base, DocumentRow, MergeDecisionLogRow, TenantRow
from kj_atlas_api.tenant_context import TenantContext


def _tenant(tenant_id: str) -> TenantContext:
    return TenantContext(
        tenant_id=tenant_id,
        membership_id=f"membership:{tenant_id}",
        resolved_by="verified_claim",
    )


def test_repository_queries_are_tenant_scoped(tmp_path) -> None:
    db_path = tmp_path / "tenant_repository.sqlite3"
    engine = create_engine(f"sqlite:///{db_path}")
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    tenant_a = _tenant("tenant-a")
    tenant_b = _tenant("tenant-b")
    try:
        with session_local() as db:
            db.add_all(
                [
                    TenantRow(
                        id=tenant_a.tenant_id,
                        display_name="Tenant A",
                        lifecycle_state="active",
                        created_at="2026-07-16T00:00:00Z",
                        updated_at="2026-07-16T00:00:00Z",
                    ),
                    TenantRow(
                        id=tenant_b.tenant_id,
                        display_name="Tenant B",
                        lifecycle_state="active",
                        created_at="2026-07-16T00:00:00Z",
                        updated_at="2026-07-16T00:00:00Z",
                    ),
                    DocumentRow(
                        id="doc-a",
                        tenant_id=tenant_a.tenant_id,
                        version=1,
                        updated_at="2026-07-16T00:00:00Z",
                        payload_json="{}",
                    ),
                    DocumentRow(
                        id="doc-b",
                        tenant_id=tenant_b.tenant_id,
                        version=1,
                        updated_at="2026-07-16T00:00:00Z",
                        payload_json="{}",
                    ),
                ]
            )
            db.commit()

            assert get_document_row(db, tenant=tenant_a, doc_id="doc-a") is not None
            assert get_document_row(db, tenant=tenant_a, doc_id="doc-b") is None
            assert [row.id for row in list_document_rows(db, tenant=tenant_a)] == ["doc-a"]
            assert [row.id for row in list_document_rows(db, tenant=tenant_b)] == ["doc-b"]
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_merge_log_queries_are_tenant_scoped(tmp_path) -> None:
    db_path = tmp_path / "tenant_merge_logs.sqlite3"
    engine = create_engine(f"sqlite:///{db_path}")
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    tenant_a = _tenant("tenant-a")
    tenant_b = _tenant("tenant-b")
    try:
        with session_local() as db:
            db.add_all(
                [
                    TenantRow(
                        id=tenant_a.tenant_id,
                        display_name="Tenant A",
                        lifecycle_state="active",
                        created_at="2026-07-16T00:00:00Z",
                        updated_at="2026-07-16T00:00:00Z",
                    ),
                    TenantRow(
                        id=tenant_b.tenant_id,
                        display_name="Tenant B",
                        lifecycle_state="active",
                        created_at="2026-07-16T00:00:00Z",
                        updated_at="2026-07-16T00:00:00Z",
                    ),
                    DocumentRow(
                        id="doc-a",
                        tenant_id=tenant_a.tenant_id,
                        version=1,
                        updated_at="2026-07-16T00:00:00Z",
                        payload_json="{}",
                    ),
                    DocumentRow(
                        id="doc-b",
                        tenant_id=tenant_b.tenant_id,
                        version=1,
                        updated_at="2026-07-16T00:00:00Z",
                        payload_json="{}",
                    ),
                    MergeDecisionLogRow(
                        tenant_id=tenant_a.tenant_id,
                        doc_id="doc-a",
                        decision_id="decision-a",
                        group_id="shared-group",
                        snapshot_version="shared-snapshot",
                        decided_at="2026-07-16T00:00:00Z",
                        payload_json="{}",
                    ),
                    MergeDecisionLogRow(
                        tenant_id=tenant_b.tenant_id,
                        doc_id="doc-b",
                        decision_id="decision-b",
                        group_id="shared-group",
                        snapshot_version="shared-snapshot",
                        decided_at="2026-07-16T00:00:00Z",
                        payload_json="{}",
                    ),
                ]
            )
            db.commit()

            group_rows = list_merge_decision_logs_by_group(
                db,
                tenant=tenant_a,
                doc_id="doc-a",
                group_id="shared-group",
            )
            snapshot_rows = list_merge_decision_logs_by_snapshot(
                db,
                tenant=tenant_a,
                doc_id="doc-a",
                snapshot_version="shared-snapshot",
            )

            assert [row.decision_id for row in group_rows] == ["decision-a"]
            assert [row.decision_id for row in snapshot_rows] == ["decision-a"]
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
