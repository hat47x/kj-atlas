from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from kj_atlas_api.models import DocumentAccessMetadataRow
from kj_atlas_api.tenant_context import TenantContext
from kj_atlas_api.tenant_db_guard import apply_database_tenant_context


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
