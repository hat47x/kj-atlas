from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from kj_atlas_api.models import DocumentAccessMetadataRow, DocumentRow
from kj_atlas_api.tenant_context import TenantContext
from kj_atlas_api.tenant_db_guard import apply_database_tenant_context


@dataclass(frozen=True, slots=True)
class DocumentAccessMetadataEntry:
    doc_id: str
    metadata: DocumentAccessMetadataRow | None


def get_document_access_metadata_row(
    db: Session,
    *,
    tenant: TenantContext,
    doc_id: str,
) -> DocumentAccessMetadataRow | None:
    apply_database_tenant_context(db=db, tenant=tenant)
    return db.scalar(
        select(DocumentAccessMetadataRow).where(
            DocumentAccessMetadataRow.tenant_id == tenant.tenant_id,
            DocumentAccessMetadataRow.doc_id == doc_id,
        )
    )


def document_access_target_exists(
    db: Session,
    *,
    tenant: TenantContext,
    doc_id: str,
) -> bool:
    apply_database_tenant_context(db=db, tenant=tenant)
    return (
        db.scalar(
            select(DocumentRow.id).where(
                DocumentRow.tenant_id == tenant.tenant_id,
                DocumentRow.id == doc_id,
            )
        )
        is not None
    )


def list_document_access_metadata_entries(
    db: Session,
    *,
    tenant: TenantContext,
    cursor: str | None = None,
    limit: int = 100,
) -> tuple[list[DocumentAccessMetadataEntry], bool]:
    """List document IDs and policy metadata without loading document payloads.

    SEC-DOC-BOUND-04: keyset pagination on the server-owned DocumentRow.id
    (ascending). `cursor` is the previous page's last document id; `limit`
    (default 100, max 500) bounds the response. Returns (entries, has_more).
    """
    apply_database_tenant_context(db=db, tenant=tenant)
    query = (
        select(DocumentRow.id, DocumentAccessMetadataRow)
        .outerjoin(
            DocumentAccessMetadataRow,
            and_(
                DocumentAccessMetadataRow.tenant_id == DocumentRow.tenant_id,
                DocumentAccessMetadataRow.doc_id == DocumentRow.id,
            ),
        )
        .where(DocumentRow.tenant_id == tenant.tenant_id)
    )
    if cursor is not None:
        query = query.where(DocumentRow.id > cursor)
    query = query.order_by(DocumentRow.id.asc()).limit(limit + 1)
    rows = db.execute(query).all()
    has_more = len(rows) > limit
    rows = rows[:limit]
    return [
        DocumentAccessMetadataEntry(doc_id=doc_id, metadata=metadata)
        for doc_id, metadata in rows
    ], has_more
