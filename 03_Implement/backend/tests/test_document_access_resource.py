from __future__ import annotations

from dataclasses import dataclass, field

from fastapi import HTTPException, Request
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from kj_atlas_api.document_access_resource import (
    ServerOwnedDocumentResourceResolver,
    SingleTenantHeaderResourceResolver,
)
from kj_atlas_api.models import (
    Base,
    DocumentAccessMetadataRow,
    DocumentRow,
    TenantRow,
)
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


def _tenant(tenant_id: str = "tenant-a") -> TenantContext:
    return TenantContext(
        tenant_id=tenant_id,
        membership_id="membership-a",
        resolved_by="verified_claim",
    )


@dataclass
class StubPolicyBindingResolver:
    values: dict[tuple[str, str, str], str]
    calls: list[tuple[str, str, str]] = field(default_factory=list)

    def resolve(
        self,
        *,
        tenant: TenantContext,
        binding_id: str,
        policy_version: str,
    ) -> str | None:
        key = (tenant.tenant_id, binding_id, policy_version)
        self.calls.append(key)
        return self.values.get(key)


class RaisingPolicyBindingResolver:
    def resolve(
        self,
        *,
        tenant: TenantContext,  # noqa: ARG002
        binding_id: str,  # noqa: ARG002
        policy_version: str,  # noqa: ARG002
    ) -> str | None:
        raise RuntimeError("secret store unavailable")


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


def test_server_owned_resolver_uses_stored_binding_and_transient_policy_ref(tmp_path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'bound-resource.sqlite3'}")
    Base.metadata.create_all(bind=engine)
    binding_resolver = StubPolicyBindingResolver(
        {("tenant-a", "binding-1", "policy-v3"): "runtime-policy-ref"}
    )
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
            db.add(
                DocumentAccessMetadataRow(
                    tenant_id="tenant-a",
                    doc_id="doc-1",
                    visibility="Org",
                    policy_binding_id="binding-1",
                    policy_version="policy-v3",
                    updated_at=TIMESTAMP,
                )
            )
            db.commit()

            resource = ServerOwnedDocumentResourceResolver(
                policy_binding_resolver=binding_resolver
            ).resolve(
                db=db,
                request=_request(visibility="Public", policy_ref="client-spoof"),
                tenant=_tenant(),
                action="read",
                doc_id="doc-1",
            )

        assert resource.visibility == "Org"
        assert resource.policy_ref == "runtime-policy-ref"
        assert resource.tenant_id == "tenant-a"
        assert binding_resolver.calls == [("tenant-a", "binding-1", "policy-v3")]
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_server_owned_metadata_isolated_for_same_doc_id_across_tenants(tmp_path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'isolated-resource.sqlite3'}")
    Base.metadata.create_all(bind=engine)
    binding_resolver = StubPolicyBindingResolver(
        {
            ("tenant-a", "binding-a", "v1"): "runtime-policy-a",
            ("tenant-b", "binding-b", "v2"): "runtime-policy-b",
        }
    )
    try:
        with Session(engine) as db:
            for tenant_id, visibility, binding_id, policy_version in (
                ("tenant-a", "Org", "binding-a", "v1"),
                ("tenant-b", "Restricted", "binding-b", "v2"),
            ):
                db.add(
                    TenantRow(
                        id=tenant_id,
                        display_name=tenant_id,
                        lifecycle_state="active",
                        created_at=TIMESTAMP,
                        updated_at=TIMESTAMP,
                    )
                )
                db.add(
                    DocumentRow(
                        tenant_id=tenant_id,
                        id="shared-doc",
                        version=1,
                        updated_at=TIMESTAMP,
                        payload_json="{}",
                    )
                )
                db.add(
                    DocumentAccessMetadataRow(
                        tenant_id=tenant_id,
                        doc_id="shared-doc",
                        visibility=visibility,
                        policy_binding_id=binding_id,
                        policy_version=policy_version,
                        updated_at=TIMESTAMP,
                    )
                )
            db.commit()

            resolver = ServerOwnedDocumentResourceResolver(
                policy_binding_resolver=binding_resolver
            )
            tenant_a_resource = resolver.resolve(
                db=db,
                request=_request(),
                tenant=_tenant("tenant-a"),
                action="read",
                doc_id="shared-doc",
            )
            tenant_b_resource = resolver.resolve(
                db=db,
                request=_request(),
                tenant=_tenant("tenant-b"),
                action="read",
                doc_id="shared-doc",
            )

        assert (tenant_a_resource.visibility, tenant_a_resource.policy_ref) == (
            "Org",
            "runtime-policy-a",
        )
        assert (tenant_b_resource.visibility, tenant_b_resource.policy_ref) == (
            "Restricted",
            "runtime-policy-b",
        )
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_public_metadata_does_not_require_policy_binding_resolution(tmp_path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'public-resource.sqlite3'}")
    Base.metadata.create_all(bind=engine)
    binding_resolver = StubPolicyBindingResolver({})
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
                    id="public-doc",
                    version=1,
                    updated_at=TIMESTAMP,
                    payload_json="{}",
                )
            )
            db.add(
                DocumentAccessMetadataRow(
                    tenant_id="tenant-a",
                    doc_id="public-doc",
                    visibility="Public",
                    policy_binding_id=None,
                    policy_version="policy-v1",
                    updated_at=TIMESTAMP,
                )
            )
            db.commit()

            resource = ServerOwnedDocumentResourceResolver(
                policy_binding_resolver=binding_resolver
            ).resolve(
                db=db,
                request=_request(visibility="Restricted", policy_ref="client-spoof"),
                tenant=_tenant(),
                action="read",
                doc_id="public-doc",
            )

        assert resource.visibility == "Public"
        assert resource.policy_ref is None
        assert binding_resolver.calls == []
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_policy_binding_failure_keeps_restricted_resource_fail_closed(tmp_path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'unavailable-binding.sqlite3'}")
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
            db.add(
                DocumentAccessMetadataRow(
                    tenant_id="tenant-a",
                    doc_id="doc-1",
                    visibility="Restricted",
                    policy_binding_id="binding-1",
                    policy_version="policy-v1",
                    updated_at=TIMESTAMP,
                )
            )
            db.commit()

            resource = ServerOwnedDocumentResourceResolver(
                policy_binding_resolver=RaisingPolicyBindingResolver()
            ).resolve(
                db=db,
                request=_request(),
                tenant=_tenant(),
                action="read",
                doc_id="doc-1",
            )

        assert resource.visibility == "Restricted"
        assert resource.policy_ref is None
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
