from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from kj_atlas_api.database_content_store import (
    DatabaseAppendOnlyLogContentStore,
    DatabaseDocumentContentStore,
)
from kj_atlas_api.models import DocumentRow, MergeDecisionLogRow
from kj_atlas_api.tenant_context import TenantContext
from kj_atlas_api.tenant_db_guard import apply_database_tenant_context


def get_document_row(
    db: Session,
    *,
    tenant: TenantContext,
    doc_id: str,
) -> DocumentRow | None:
    stored = DatabaseDocumentContentStore(db).load(tenant=tenant, doc_id=doc_id)
    return None if stored is None else stored.row


def list_document_rows(
    db: Session,
    *,
    tenant: TenantContext,
) -> Sequence[DocumentRow]:
    apply_database_tenant_context(db=db, tenant=tenant)
    return db.scalars(
        select(DocumentRow)
        .where(DocumentRow.tenant_id == tenant.tenant_id)
        .order_by(DocumentRow.id.asc())
    ).all()


def list_merge_decision_logs_by_group(
    db: Session,
    *,
    tenant: TenantContext,
    doc_id: str,
    group_id: str,
) -> Sequence[MergeDecisionLogRow]:
    return [
        stored.row
        for stored in DatabaseAppendOnlyLogContentStore(db).list_by_group(
            tenant=tenant,
            doc_id=doc_id,
            group_id=group_id,
        )
    ]


def list_merge_decision_logs_by_snapshot(
    db: Session,
    *,
    tenant: TenantContext,
    doc_id: str,
    snapshot_version: str,
) -> Sequence[MergeDecisionLogRow]:
    return [
        stored.row
        for stored in DatabaseAppendOnlyLogContentStore(db).list_by_snapshot(
            tenant=tenant,
            doc_id=doc_id,
            snapshot_version=snapshot_version,
        )
    ]
