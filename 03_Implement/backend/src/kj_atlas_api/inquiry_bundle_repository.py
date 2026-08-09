from __future__ import annotations

from sqlalchemy.orm import Session

from kj_atlas_api.database_content_store import DatabaseBundleContentStore
from kj_atlas_api.models import InquiryBundleRow
from kj_atlas_api.tenant_context import TenantContext


def get_inquiry_bundle_row(
    db: Session,
    *,
    tenant: TenantContext,
    journey_id: str,
) -> InquiryBundleRow | None:
    stored = DatabaseBundleContentStore(db).load(tenant=tenant, journey_id=journey_id)
    return None if stored is None else stored.row


def delete_inquiry_bundle(
    db: Session,
    *,
    tenant: TenantContext,
    journey_id: str,
) -> bool:
    """Delete exactly one complete journey without looking at its payload."""
    return DatabaseBundleContentStore(db).delete(tenant=tenant, journey_id=journey_id)
