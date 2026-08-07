from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from kj_atlas_api.inquiry_bundle_repository import (
    delete_inquiry_bundle,
    get_inquiry_bundle_row,
)
from kj_atlas_api.models import Base, InquiryBundleRow, TenantRow
from kj_atlas_api.tenant_context import TenantContext


def _tenant(tenant_id: str) -> TenantContext:
    return TenantContext(
        tenant_id=tenant_id,
        membership_id=f"membership-{tenant_id}",
        resolved_by="verified_claim",
    )


def test_repository_uses_tenant_and_journey_as_the_only_lookup_key(tmp_path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'inquiry-repository.sqlite3'}")
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)
    try:
        with session_local() as db:
            db.add_all(
                [
                    TenantRow(id="tenant-a", display_name="A", lifecycle_state="active", created_at="now", updated_at="now"),
                    TenantRow(id="tenant-b", display_name="B", lifecycle_state="active", created_at="now", updated_at="now"),
                    InquiryBundleRow(tenant_id="tenant-a", journey_id="same-id", payload_json='{"owner":"a"}', updated_at="now"),
                    InquiryBundleRow(tenant_id="tenant-b", journey_id="same-id", payload_json='{"owner":"b"}', updated_at="now"),
                ]
            )
            db.commit()

            tenant_a_row = get_inquiry_bundle_row(db, tenant=_tenant("tenant-a"), journey_id="same-id")
            tenant_b_row = get_inquiry_bundle_row(db, tenant=_tenant("tenant-b"), journey_id="same-id")
            missing = get_inquiry_bundle_row(db, tenant=_tenant("tenant-a"), journey_id="other-id")
            assert delete_inquiry_bundle(db, tenant=_tenant("tenant-a"), journey_id="same-id")
            db.commit()
            remaining = get_inquiry_bundle_row(db, tenant=_tenant("tenant-b"), journey_id="same-id")

        assert tenant_a_row is not None
        assert tenant_a_row.payload_json == '{"owner":"a"}'
        assert tenant_b_row is not None
        assert tenant_b_row.payload_json == '{"owner":"b"}'
        assert missing is None
        assert remaining is not None
        assert remaining.payload_json == '{"owner":"b"}'
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
