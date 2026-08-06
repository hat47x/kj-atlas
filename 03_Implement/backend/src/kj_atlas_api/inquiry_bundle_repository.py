from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from kj_atlas_api.models import InquiryBundleRow
from kj_atlas_api.tenant_context import TenantContext
from kj_atlas_api.tenant_db_guard import apply_database_tenant_context


def get_inquiry_bundle_row(
    db: Session,
    *,
    tenant: TenantContext,
    journey_id: str,
) -> InquiryBundleRow | None:
    apply_database_tenant_context(db=db, tenant=tenant)
    return db.scalar(
        select(InquiryBundleRow).where(
            InquiryBundleRow.tenant_id == tenant.tenant_id,
            InquiryBundleRow.journey_id == journey_id,
        )
    )


def delete_inquiry_bundle(
    db: Session,
    *,
    tenant: TenantContext,
    journey_id: str,
) -> bool:
    """Delete exactly one complete journey without looking at its payload."""
    apply_database_tenant_context(db=db, tenant=tenant)
    result = db.execute(
        delete(InquiryBundleRow).where(
            InquiryBundleRow.tenant_id == tenant.tenant_id,
            InquiryBundleRow.journey_id == journey_id,
        )
    )
    return result.rowcount == 1
