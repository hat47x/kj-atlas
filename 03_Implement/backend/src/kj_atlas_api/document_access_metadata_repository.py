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
) -> tuple[DocumentAccessMetadataEntry, ...]:
    """List document IDs and policy metadata without loading document payloads."""
    apply_database_tenant_context(db=db, tenant=tenant)
    rows = db.execute(
        select(DocumentRow.id, DocumentAccessMetadataRow)
        .outerjoin(
            DocumentAccessMetadataRow,
            and_(
                DocumentAccessMetadataRow.tenant_id == DocumentRow.tenant_id,
                DocumentAccessMetadataRow.doc_id == DocumentRow.id,
            ),
        )
        .where(DocumentRow.tenant_id == tenant.tenant_id)
        .order_by(DocumentRow.id.asc())
    ).all()
    return tuple(
        DocumentAccessMetadataEntry(doc_id=doc_id, metadata=metadata)
        for doc_id, metadata in rows
    )
