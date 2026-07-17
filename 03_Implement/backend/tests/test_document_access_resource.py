from __future__ import annotations

from fastapi import HTTPException, Request
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from kj_atlas_api.document_access_resource import (
    ServerOwnedDocumentResourceResolver,
    SingleTenantHeaderResourceResolver,
)
from kj_atlas_api.models import Base, DocumentRow, TenantRow
from kj_atlas_api.tenant_context import TenantContext


TIMESTAMP = "2026-07-17T00:00:00Z"


def _request(*, visibility: str = "Public", policy_ref: str = "client-policy") -> Request:
    return Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/docs/doc-1",
            "headers": [
                (b"x-doc-visibility", visibility.encode()),
                (b"x-policy-ref", policy_ref.encode()),
            ],
        }
    )


def _tenant() -> TenantContext:
    return TenantContext(
        tenant_id="tenant-a",
        membership_id="membership-a",
        resolved_by="verified_claim",
    )


def test_single_tenant_resolver_preserves_legacy_header_contract() -> None:
    resolver = SingleTenantHeaderResourceResolver()

    resource = resolver.resolve(
        db=None,  # type: ignore[arg-type]
        request=_request(visibility="Org", policy_ref=" policy-1 "),
        tenant=_tenant(),
        action="read",
        doc_id="doc-1",
    )

    assert resource.visibility == "Org"
    assert resource.policy_ref == "policy-1"
    assert resource.tenant_id == "tenant-a"


def test_server_owned_resolver_ignores_client_policy_headers(tmp_path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'resource.sqlite3'}")
    Base.metadata.create_all(bind=engine)
    try:
        with Session(engine) as db:
            db.add(
                TenantRow(
                    id="tenant-a",
                    display_name="Tenant A",
                    lifecycle_state="active",
                    created_at=TIMESTAMP,
                    updated_at=TIMESTAMP,
                )
            )
            db.add(
                DocumentRow(
                    tenant_id="tenant-a",
                    id="doc-1",
                    version=1,
                    updated_at=TIMESTAMP,
                    payload_json="{}",
                )
            )
            db.commit()

            resource = ServerOwnedDocumentResourceResolver().resolve(
                db=db,
                request=_request(),
                tenant=_tenant(),
                action="read",
                doc_id="doc-1",
            )

        assert resource.visibility == "Restricted"
        assert resource.policy_ref is None
        assert resource.tenant_id == "tenant-a"
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_server_owned_resolver_returns_not_found_before_pdp(tmp_path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'missing.sqlite3'}")
    Base.metadata.create_all(bind=engine)
    try:
        with Session(engine) as db:
            try:
                ServerOwnedDocumentResourceResolver().resolve(
                    db=db,
                    request=_request(),
                    tenant=_tenant(),
                    action="read",
                    doc_id="missing",
                )
            except HTTPException as exc:
                assert exc.status_code == 404
                assert exc.detail == "Document not found"
            else:
                raise AssertionError("missing document must fail before PDP")
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_server_owned_resolver_scopes_new_write_to_active_tenant(tmp_path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'new-write.sqlite3'}")
    Base.metadata.create_all(bind=engine)
    try:
        with Session(engine) as db:
            resource = ServerOwnedDocumentResourceResolver().resolve(
                db=db,
                request=_request(),
                tenant=_tenant(),
                action="write",
                doc_id="new-doc",
            )

        assert resource.visibility == "Restricted"
        assert resource.policy_ref is None
        assert resource.tenant_id == "tenant-a"
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
