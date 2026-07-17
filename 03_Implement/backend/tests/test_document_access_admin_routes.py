from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass

import pytest
from fastapi import Request
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker

from kj_atlas_api.access_control import AuthContext
from kj_atlas_api.auth_context import ResolvedIdentity
from kj_atlas_api.db import get_db
from kj_atlas_api.main import app
from kj_atlas_api.models import (
    Base,
    DocumentAccessAdminAuditEventRow,
    DocumentAccessMetadataRow,
    DocumentRow,
    TenantMembershipRow,
    TenantRow,
    UserRow,
)
from kj_atlas_api.session_context import CapabilitySnapshot
from kj_atlas_api.tenant_context import (
    SingleTenantContextResolver,
    TenantContext,
    select_active_tenant_context,
)


TIMESTAMP = "2026-07-17T00:00:00Z"


@dataclass
class StaticIdentityResolver:
    principal_id: str = "user-1"

    def resolve(self, *, db: Session, request: Request) -> ResolvedIdentity:  # noqa: ARG002
        actor_ref = f"user:{self.principal_id}"
        return ResolvedIdentity(
            user_id=self.principal_id,
            reviewer_ref=actor_ref,
            owner_ref=actor_ref,
            auth_context=AuthContext(
                actor_ref=actor_ref,
                user_id=self.principal_id,
                trace_id=None,
            ),
        )


@dataclass
class MutableTenantResolver:
    tenant_id: str = "tenant-a"
    resolved_by: str = "verified_claim"

    def resolve(self, *, db: Session, user_id: str | None) -> TenantContext:
        if user_id is not None and self.resolved_by in {
            "verified_claim",
            "trusted_host_mapping",
        }:
            return select_active_tenant_context(
                db=db,
                user_id=user_id,
                tenant_id=self.tenant_id,
                resolved_by=self.resolved_by,  # type: ignore[arg-type]
            )
        return TenantContext(
            tenant_id=self.tenant_id,
            membership_id=f"membership-{self.tenant_id}",
            resolved_by=self.resolved_by,  # type: ignore[arg-type]
        )


@dataclass
class MutableCapabilityResolver:
    capabilities: tuple[str, ...] = ("document.policy.manage",)
    capability_version: str = "capability-v1"

    def resolve(
        self,
        *,
        db: Session,  # noqa: ARG002
        principal_id: str,  # noqa: ARG002
        tenant: TenantContext,  # noqa: ARG002
    ) -> CapabilitySnapshot:
        return CapabilitySnapshot(
            effective_capabilities=self.capabilities,
            capability_version=self.capability_version,
        )


def _document(*, tenant_id: str, doc_id: str, title: str) -> DocumentRow:
    return DocumentRow(
        tenant_id=tenant_id,
        id=doc_id,
        version=1,
        updated_at=TIMESTAMP,
        payload_json=(
            '{"title":"' + title + '","cards":[{"text":"classified body"}]}'
        ),
    )


def _seed(db: Session) -> None:
    db.add(
        UserRow(
            id="user-1",
            display_name="Hidden User",
            email="hidden@example.invalid",
            lifecycle_state="active",
            created_at=TIMESTAMP,
            updated_at=TIMESTAMP,
        )
    )
    for tenant_id in ("tenant-a", "tenant-b"):
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
            TenantMembershipRow(
                tenant_id=tenant_id,
                user_id="user-1",
                lifecycle_state="active",
                created_at=TIMESTAMP,
                updated_at=TIMESTAMP,
            )
        )
    db.add_all(
        [
            _document(
                tenant_id="tenant-a",
                doc_id="shared-doc",
                title="Tenant A secret title",
            ),
            _document(
                tenant_id="tenant-a",
                doc_id="draft-doc",
                title="Draft secret title",
            ),
            _document(
                tenant_id="tenant-b",
                doc_id="shared-doc",
                title="Tenant B secret title",
            ),
            _document(
                tenant_id="tenant-b",
                doc_id="b-only",
                title="Tenant B only secret title",
            ),
        ]
    )
    db.add_all(
        [
            DocumentAccessMetadataRow(
                tenant_id="tenant-a",
                doc_id="shared-doc",
                visibility="Org",
                policy_binding_id="binding-a",
                policy_version="policy-v1",
                updated_at=TIMESTAMP,
            ),
            DocumentAccessMetadataRow(
                tenant_id="tenant-b",
                doc_id="shared-doc",
                visibility="Public",
                policy_binding_id=None,
                policy_version="policy-v8",
                updated_at=TIMESTAMP,
            ),
        ]
    )
    db.commit()


@contextmanager
def _tenant_admin_client(
    tmp_path,
) -> Iterator[
    tuple[
        TestClient,
        sessionmaker[Session],
        MutableTenantResolver,
        MutableCapabilityResolver,
    ]
]:
    engine = create_engine(f"sqlite:///{tmp_path / 'document-access-admin.sqlite3'}")
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)
    with session_local() as db:
        _seed(db)

    def _get_test_db():
        db = session_local()
        try:
            yield db
        finally:
            db.close()

    tenant_resolver = MutableTenantResolver()
    capability_resolver = MutableCapabilityResolver()
    app.dependency_overrides[get_db] = _get_test_db
    try:
        with TestClient(app) as client:
            client.app.state.saas_identity_context_resolver = StaticIdentityResolver()
            client.app.state.tenant_context_resolver = tenant_resolver
            client.app.state.tenant_capability_resolver = capability_resolver
            yield client, session_local, tenant_resolver, capability_resolver
    finally:
        app.dependency_overrides.clear()
        app.state.saas_identity_context_resolver = None
        app.state.tenant_capability_resolver = None
        app.state.tenant_context_resolver = SingleTenantContextResolver()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def _revision_for(client: TestClient, doc_id: str) -> str:
    response = client.get(f"/tenant-admin/document-access/{doc_id}")
    assert response.status_code == 200
    return response.json()["revision"]


def test_management_api_is_closed_without_trusted_saas_identity_adapter(tmp_path) -> None:
    with _tenant_admin_client(tmp_path) as fixture:
        client, _, _, _ = fixture
        client.app.state.saas_identity_context_resolver = None

        response = client.get("/tenant-admin/document-access")

    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "tenant_admin_auth_unavailable"


@pytest.mark.parametrize("capabilities", [("document.write",), ("tenant.provision",)])
def test_management_requires_independent_document_policy_capability(
    tmp_path,
    capabilities: tuple[str, ...],
) -> None:
    with _tenant_admin_client(tmp_path) as fixture:
        client, _, _, capability_resolver = fixture
        capability_resolver.capabilities = capabilities

        response = client.get(
            "/tenant-admin/document-access",
            headers={"x-auth-roles": "admin", "x-auth-groups": "platform-operators"},
        )

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "document_policy_manage_required"


def test_management_rejects_single_tenant_compatibility_context(tmp_path) -> None:
    with _tenant_admin_client(tmp_path) as fixture:
        client, _, tenant_resolver, _ = fixture
        tenant_resolver.resolved_by = "single_tenant_adapter"

        response = client.get("/tenant-admin/document-access")

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "tenant_context_untrusted"


def test_list_is_tenant_scoped_and_omits_document_content_and_binding_id(tmp_path) -> None:
    with _tenant_admin_client(tmp_path) as fixture:
        client, _, tenant_resolver, _ = fixture

        tenant_a = client.get("/tenant-admin/document-access")
        tenant_resolver.tenant_id = "tenant-b"
        tenant_b = client.get("/tenant-admin/document-access")

    assert tenant_a.status_code == 200
    assert [item["docId"] for item in tenant_a.json()["items"]] == [
        "draft-doc",
        "shared-doc",
    ]
    assert tenant_a.json()["items"][0]["visibility"] == "Restricted"
    assert tenant_a.json()["items"][0]["bindingStatus"] == "unconfigured"
    assert tenant_a.json()["items"][1]["visibility"] == "Org"
    assert [item["docId"] for item in tenant_b.json()["items"]] == [
        "b-only",
        "shared-doc",
    ]
    assert tenant_b.json()["items"][1]["visibility"] == "Public"
    serialized = tenant_a.text + tenant_b.text
    assert "secret title" not in serialized
    assert "classified body" not in serialized
    assert "binding-a" not in serialized
    assert "policyBindingId" not in serialized
    assert "tenantId" not in serialized


def test_detail_exposes_only_editable_nonsecret_binding_metadata(tmp_path) -> None:
    with _tenant_admin_client(tmp_path) as fixture:
        client, _, _, _ = fixture

        response = client.get("/tenant-admin/document-access/shared-doc")

    assert response.status_code == 200
    assert response.json()["policyBindingId"] == "binding-a"
    assert response.json()["policyVersion"] == "policy-v1"
    assert response.headers["etag"] == f'"{response.json()["revision"]}"'
    assert "title" not in response.text.lower()
    assert "cards" not in response.text.lower()


def test_invalid_or_secret_shaped_payload_is_rejected_without_reflection(tmp_path) -> None:
    with _tenant_admin_client(tmp_path) as fixture:
        client, session_local, _, _ = fixture
        revision = _revision_for(client, "draft-doc")

        response = client.put(
            "/tenant-admin/document-access/draft-doc",
            headers={"If-Match": f'"{revision}"'},
            json={
                "visibility": "Restricted",
                "policyBindingId": "binding-new",
                "policyVersion": "policy-v2",
                "policyRef": "super-secret-runtime-token",
            },
        )

        with session_local() as db:
            metadata = db.get(DocumentAccessMetadataRow, ("tenant-a", "draft-doc"))
            audit_count = db.scalar(select(func.count(DocumentAccessAdminAuditEventRow.event_id)))

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "invalid_document_access_settings"
    assert "super-secret-runtime-token" not in response.text
    assert metadata is None
    assert audit_count == 0


def test_update_is_tenant_scoped_and_writes_minimal_transactional_audit(tmp_path) -> None:
    with _tenant_admin_client(tmp_path) as fixture:
        client, session_local, _, _ = fixture
        revision = _revision_for(client, "shared-doc")

        response = client.put(
            "/tenant-admin/document-access/shared-doc",
            headers={"If-Match": f'"{revision}"'},
            json={
                "visibility": "Restricted",
                "policyBindingId": "binding-a-next",
                "policyVersion": "policy-v2",
            },
        )

        with session_local() as db:
            tenant_a = db.get(DocumentAccessMetadataRow, ("tenant-a", "shared-doc"))
            tenant_b = db.get(DocumentAccessMetadataRow, ("tenant-b", "shared-doc"))
            events = db.scalars(select(DocumentAccessAdminAuditEventRow)).all()

    assert response.status_code == 200
    assert response.json()["item"]["visibility"] == "Restricted"
    assert response.json()["receipt"]["capabilityVersion"] == "capability-v1"
    assert response.headers["etag"] == f'"{response.json()["item"]["revision"]}"'
    assert tenant_a is not None
    assert tenant_a.policy_binding_id == "binding-a-next"
    assert tenant_b is not None
    assert tenant_b.visibility == "Public"
    assert tenant_b.policy_binding_id is None
    assert len(events) == 1
    assert events[0].tenant_id == "tenant-a"
    assert events[0].principal_id == "user-1"
    assert events[0].doc_id == "shared-doc"
    assert events[0].action == "document.policy.update"
    assert events[0].decision == "allowed"
    assert events[0].policy_version == "policy-v2"
    assert events[0].capability_version == "capability-v1"
    assert not hasattr(events[0], "policy_binding_id")
    assert "binding-a-next" not in str(events[0].__dict__)


def test_update_requires_precondition_and_stale_revision_does_not_write_audit(tmp_path) -> None:
    with _tenant_admin_client(tmp_path) as fixture:
        client, session_local, _, _ = fixture
        revision = _revision_for(client, "draft-doc")
        payload = {
            "visibility": "Org",
            "policyBindingId": "binding-draft",
            "policyVersion": "policy-v3",
        }

        missing_precondition = client.put(
            "/tenant-admin/document-access/draft-doc",
            json=payload,
        )
        first = client.put(
            "/tenant-admin/document-access/draft-doc",
            headers={"If-Match": revision},
            json=payload,
        )
        stale = client.put(
            "/tenant-admin/document-access/draft-doc",
            headers={"If-Match": revision},
            json={**payload, "policyVersion": "policy-v4"},
        )

        with session_local() as db:
            metadata = db.get(DocumentAccessMetadataRow, ("tenant-a", "draft-doc"))
            audit_count = db.scalar(select(func.count(DocumentAccessAdminAuditEventRow.event_id)))

    assert missing_precondition.status_code == 428
    assert first.status_code == 200
    assert stale.status_code == 409
    assert stale.json()["detail"]["code"] == "document_access_conflict"
    assert metadata is not None
    assert metadata.policy_version == "policy-v3"
    assert audit_count == 1


def test_other_tenant_document_id_is_not_disclosed(tmp_path) -> None:
    with _tenant_admin_client(tmp_path) as fixture:
        client, _, _, _ = fixture

        response = client.get("/tenant-admin/document-access/b-only")

    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found"
