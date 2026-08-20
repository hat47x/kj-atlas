from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from kj_atlas_api.access_control import (
    AccessControlInvalidPolicyError,
    AccessControlUnreachableError,
    AccessDecision,
    AuthContext,
)
from kj_atlas_api.db import get_db
from kj_atlas_api.main import app
from kj_atlas_api.models import LOCAL_DEFAULT_TENANT_ID, Base
from kj_atlas_api.tenant_context import TenantContext


class DenyAllAdapter:
    name = "deny-all"

    def authorize(self, request):  # noqa: ANN001
        return AccessDecision(allow=False, reason=f"blocked:{request.action}")


class AllowAllAdapter:
    name = "allow-all"

    def authorize(self, request):  # noqa: ANN001
        return AccessDecision(allow=True)


class UnreachableAdapter:
    name = "unreachable"

    def authorize(self, request):  # noqa: ANN001
        raise AccessControlUnreachableError("timeout")


class InvalidPolicyAdapter:
    name = "invalid-policy"

    def authorize(self, request):  # noqa: ANN001
        raise AccessControlInvalidPolicyError("bad signature")


class CrashAdapter:
    name = "crash"

    def authorize(self, request):  # noqa: ANN001
        raise RuntimeError("unexpected adapter exception")


@contextmanager
def _sqlite_client(tmp_path) -> Iterator[TestClient]:
    db_path = tmp_path / "docs_access_control.sqlite3"
    engine = create_engine(f"sqlite:///{db_path}")
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    Base.metadata.create_all(bind=engine)

    def _get_test_db():
        db = session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _get_test_db
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def _sample_payload(doc_id: str) -> dict:
    return {
        "version": 1,
        "id": doc_id,
        "title": "access-test",
        "createdAt": "2026-02-11T00:00:00Z",
        "updatedAt": "2026-02-11T00:00:00Z",
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
        "cards": [{"id": "card-1", "text": "alpha", "x": 0, "y": 0}],
        "edges": [],
        "islands": [],
    }


def test_adapter_unset_keeps_existing_docs_roundtrip(tmp_path) -> None:
    with _sqlite_client(tmp_path) as client:
        client.app.state.access_control_adapter = None
        put_resp = client.put("/docs/doc-compat", json=_sample_payload("doc-compat"))
        assert put_resp.status_code == 200

        get_resp = client.get("/docs/doc-compat")
        assert get_resp.status_code == 200


def test_tenant_scoped_profile_denies_read_when_adapter_is_missing(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Same request as the roundtrip above -- adapter unset, document present in
    # the caller's own tenant -- so a 404 or a tenant-boundary reason cannot be
    # mistaken for the denial under test. Only the runtime profile differs.
    monkeypatch.setattr(
        "kj_atlas_api.routes.docs.resolve_trusted_saas_request_session",
        lambda **_: SimpleNamespace(
            identity=SimpleNamespace(
                auth_context=AuthContext(actor_ref="user-1", user_id="user-1"),
            ),
            tenant=TenantContext(
                tenant_id=LOCAL_DEFAULT_TENANT_ID,
                membership_id="membership-1",
                resolved_by="verified_claim",
            ),
            session=SimpleNamespace(tenant_session_version="session-v2"),
        ),
    )

    with _sqlite_client(tmp_path) as client:
        client.app.state.access_control_adapter = None
        seed_resp = client.put(
            "/docs/doc-adapter-missing",
            json=_sample_payload("doc-adapter-missing"),
        )
        assert seed_resp.status_code == 200

        original_runtime_profile = client.app.state.runtime_profile
        try:
            client.app.state.runtime_profile = "saas-multitenant"
            read_resp = client.get(
                "/docs/doc-adapter-missing",
                headers={"KJ-Atlas-Tenant-Session-Version": "session-v2"},
            )
            write_resp = client.put(
                "/docs/doc-adapter-missing",
                json=_sample_payload("doc-adapter-missing"),
                headers={"KJ-Atlas-Tenant-Session-Version": "session-v2"},
            )
        finally:
            client.app.state.runtime_profile = original_runtime_profile

    assert read_resp.status_code == 403
    assert read_resp.json()["detail"] == "Access denied: adapter_missing"
    assert "access-test" not in read_resp.text
    assert "alpha" not in read_resp.text
    assert write_resp.status_code == 403
    assert write_resp.json()["detail"] == "Access denied: adapter_missing"


def test_fail_safe_deny_when_policy_ref_missing_for_restricted_visibility(tmp_path) -> None:
    with _sqlite_client(tmp_path) as client:
        client.app.state.access_control_adapter = AllowAllAdapter()
        client.app.state.access_control_fail_safe_mode = "deny"

        response = client.get(
            "/docs/doc-restricted",
            headers={"x-doc-visibility": "Restricted"},
        )

    assert response.status_code == 403
    assert response.json()["detail"] == "Access denied: policy_ref_missing"


def test_fail_safe_visibility_header_is_trimmed_before_policy_ref_guard(tmp_path) -> None:
    with _sqlite_client(tmp_path) as client:
        client.app.state.access_control_adapter = AllowAllAdapter()
        client.app.state.access_control_fail_safe_mode = "deny"

        response = client.get(
            "/docs/doc-restricted-trimmed",
            headers={"x-doc-visibility": "  Restricted  "},
        )

    assert response.status_code == 403
    assert response.json()["detail"] == "Access denied: policy_ref_missing"


def test_fail_safe_read_only_blocks_write_export_but_allows_read(tmp_path) -> None:
    with _sqlite_client(tmp_path) as client:
        client.app.state.access_control_adapter = AllowAllAdapter()
        client.app.state.access_control_fail_safe_mode = "read_only"
        client.put("/docs/doc-ro", json=_sample_payload("doc-ro"))

        read_resp = client.get(
            "/docs/doc-ro",
            headers={"x-doc-visibility": "Restricted"},
        )
        write_resp = client.put(
            "/docs/doc-ro",
            json=_sample_payload("doc-ro"),
            headers={"x-doc-visibility": "Restricted"},
        )
        export_resp = client.post(
            "/docs/doc-ro/export-audit",
            json={"safeMode": True, "exportKind": "bundle"},
            headers={"x-doc-visibility": "Restricted"},
        )

    assert read_resp.status_code == 200
    assert write_resp.status_code == 403
    assert export_resp.status_code == 403


def test_fail_safe_unreachable_policy_ref_blocks_export_with_reason(tmp_path) -> None:
    with _sqlite_client(tmp_path) as client:
        client.app.state.access_control_adapter = UnreachableAdapter()
        client.app.state.access_control_fail_safe_mode = "deny"

        response = client.post(
            "/docs/doc-unreachable/export-audit",
            json={"safeMode": False, "exportKind": "bundle"},
            headers={"x-doc-visibility": "Restricted", "x-policy-ref": "org-policy-v1"},
        )

    assert response.status_code == 403
    assert response.json()["detail"] == "Access denied: policy_ref_unreachable"


def test_fail_safe_invalid_policy_ref_blocks_write_with_reason(tmp_path) -> None:
    with _sqlite_client(tmp_path) as client:
        client.app.state.access_control_adapter = InvalidPolicyAdapter()
        client.app.state.access_control_fail_safe_mode = "deny"

        response = client.put(
            "/docs/doc-invalid",
            json=_sample_payload("doc-invalid"),
            headers={"x-doc-visibility": "Org", "x-policy-ref": "org-policy-v1"},
        )

    assert response.status_code == 403
    assert response.json()["detail"] == "Access denied: policy_ref_invalid"


def test_fail_safe_adapter_exception_blocks_read_with_reason(tmp_path) -> None:
    with _sqlite_client(tmp_path) as client:
        client.app.state.access_control_adapter = CrashAdapter()
        client.app.state.access_control_fail_safe_mode = "deny"

        response = client.get(
            "/docs/doc-crash",
            headers={"x-doc-visibility": "Org", "x-policy-ref": "org-policy-v1"},
        )

    assert response.status_code == 403
    assert response.json()["detail"] == "Access denied: adapter_error"


def test_safe_mode_priority_blocks_export_before_adapter_allow(tmp_path) -> None:
    with _sqlite_client(tmp_path) as client:
        client.app.state.access_control_adapter = AllowAllAdapter()
        client.app.state.access_control_fail_safe_mode = "read_only"

        response = client.post(
            "/docs/doc-safe-mode/export-audit",
            json={"safeMode": True, "exportKind": "bundle"},
            headers={"x-doc-visibility": "Public", "x-policy-ref": "public-policy-v1"},
        )

    assert response.status_code == 403
    assert response.json()["detail"] == "Access denied: safe_mode"


def test_read_only_priority_blocks_write_before_adapter_allow(tmp_path) -> None:
    with _sqlite_client(tmp_path) as client:
        client.app.state.access_control_adapter = AllowAllAdapter()
        client.app.state.access_control_fail_safe_mode = "read_only"

        response = client.put(
            "/docs/doc-read-only",
            json=_sample_payload("doc-read-only"),
            headers={"x-read-only": "true", "x-doc-visibility": "Public", "x-policy-ref": "public-policy-v1"},
        )

    assert response.status_code == 403
    assert response.json()["detail"] == "Access denied: read_only"


@pytest.mark.parametrize("visibility", ["Public", "Unlisted", "Org", "Restricted"])
def test_safe_mode_and_read_only_priority_remains_stronger_than_visibility_label(tmp_path, visibility: str) -> None:
    with _sqlite_client(tmp_path) as client:
        client.app.state.access_control_adapter = AllowAllAdapter()
        client.app.state.access_control_fail_safe_mode = "read_only"

        export_resp = client.post(
            "/docs/doc-priority/export-audit",
            json={"safeMode": True, "exportKind": "bundle"},
            headers={"x-doc-visibility": visibility, "x-policy-ref": "policy-v1"},
        )
        write_resp = client.put(
            "/docs/doc-priority",
            json=_sample_payload("doc-priority"),
            headers={"x-read-only": "true", "x-doc-visibility": visibility, "x-policy-ref": "policy-v1"},
        )

    assert export_resp.status_code == 403
    assert export_resp.json()["detail"] == "Access denied: safe_mode"
    assert write_resp.status_code == 403
    assert write_resp.json()["detail"] == "Access denied: read_only"


def test_adapter_denial_prevents_role_header_privilege_escalation(tmp_path) -> None:
    with _sqlite_client(tmp_path) as client:
        client.app.state.access_control_adapter = DenyAllAdapter()
        client.app.state.access_control_fail_safe_mode = "read_only"

        response = client.put(
            "/docs/doc-escalation",
            json=_sample_payload("doc-escalation"),
            headers={
                "x-auth-roles": "admin,superuser",
                "x-auth-groups": "security",
                "x-doc-visibility": "Org",
                "x-policy-ref": "policy-org-1",
            },
        )

    assert response.status_code == 403
    assert "blocked:write" in response.json()["detail"]


class CapturingAdapter:
    """Records the last AccessRequest so tests can assert what reached the PDP."""

    name = "capturing"
    last_request: SimpleNamespace | None = None

    def authorize(self, request):  # noqa: ANN001
        CapturingAdapter.last_request = request
        return AccessDecision(allow=True)


def test_client_supplied_roles_groups_never_reach_the_pdp(tmp_path) -> None:
    """SEC-AUTH-ATTRIB-01 AC-2/AC-3: x-auth-roles / x-auth-groups are client
    supplied; the server must not forward them to its own authorization service.
    The PDP receives the verified identity's roles/groups — empty today, and
    never the header values."""
    CapturingAdapter.last_request = None
    with _sqlite_client(tmp_path) as client:
        client.app.state.access_control_adapter = CapturingAdapter()
        resp = client.put(
            "/docs/doc-roles",
            json=_sample_payload("doc-roles"),
            headers={
                "x-auth-roles": "admin,superuser",
                "x-auth-groups": "security",
            },
        )
        assert resp.status_code == 200, resp.text

    assert CapturingAdapter.last_request is not None
    captured_auth = CapturingAdapter.last_request.auth
    assert captured_auth.roles == ()
    assert captured_auth.groups == ()


def test_archive_denied_by_adapter(tmp_path) -> None:
    """SEC-DOC-BOUND-06: archive is write-equivalent (it locks the document via
    the ADR-0073 D2=A 423 gate) and must be denied the same way PUT is."""
    with _sqlite_client(tmp_path) as client:
        seed_resp = client.put("/docs/doc-archive-denied", json=_sample_payload("doc-archive-denied"))
        assert seed_resp.status_code == 200, seed_resp.text

        client.app.state.access_control_adapter = DenyAllAdapter()
        client.app.state.access_control_fail_safe_mode = "read_only"
        response = client.post("/docs/doc-archive-denied/archive")

    assert response.status_code == 403
    assert "blocked:write" in response.json()["detail"]


def test_unarchive_denied_by_adapter(tmp_path) -> None:
    """SEC-DOC-BOUND-06: unarchive must pass the same capability check as
    archive/PUT, not just a tenant-match check."""
    with _sqlite_client(tmp_path) as client:
        seed_resp = client.put("/docs/doc-unarchive-denied", json=_sample_payload("doc-unarchive-denied"))
        assert seed_resp.status_code == 200, seed_resp.text
        archive_resp = client.post("/docs/doc-unarchive-denied/archive")
        assert archive_resp.status_code == 204, archive_resp.text

        client.app.state.access_control_adapter = DenyAllAdapter()
        client.app.state.access_control_fail_safe_mode = "read_only"
        response = client.post("/docs/doc-unarchive-denied/unarchive")

    assert response.status_code == 403
    assert "blocked:write" in response.json()["detail"]


def _provision(client: TestClient, *, external_uid: str) -> None:
    provision = client.post(
        "/admin/provision/users",
        json={"provider": "oidc", "externalUid": external_uid, "displayName": external_uid},
    )
    assert provision.status_code == 201, provision.text


def _insert_access_metadata(tmp_path, *, doc_id: str, visibility: str) -> None:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from kj_atlas_api.models import DocumentAccessMetadataRow

    engine = create_engine(f"sqlite:///{tmp_path / 'docs_access_control.sqlite3'}")
    session_local = sessionmaker(bind=engine)
    with session_local() as db:
        db.add(
            DocumentAccessMetadataRow(
                tenant_id="local-default",
                doc_id=doc_id,
                visibility=visibility,
                policy_binding_id=None if visibility in ("Public", "Unlisted") else "policy-1",
                policy_version="v1",
                updated_at="2026-08-19T00:00:00Z",
            )
        )
        db.commit()
    engine.dispose()


def test_list_hides_restricted_documents_from_non_creators_when_adapter_is_real(tmp_path) -> None:
    """SEC-DOC-BOUND-06: with a real (non-noop) adapter configured, a
    Restricted document is hidden from the list for anyone but its creator."""
    with _sqlite_client(tmp_path) as client:
        client.app.state.access_control_adapter = AllowAllAdapter()
        _provision(client, external_uid="alpha")
        _provision(client, external_uid="beta")

        put_resp = client.put(
            "/docs/doc-restricted-list",
            json=_sample_payload("doc-restricted-list"),
            headers={"x-forwarded-user": "alpha", "x-auth-provider": "oidc"},
        )
        assert put_resp.status_code == 200, put_resp.text
        _insert_access_metadata(tmp_path, doc_id="doc-restricted-list", visibility="Restricted")

        as_creator = client.get(
            "/docs", headers={"x-forwarded-user": "alpha", "x-auth-provider": "oidc"}
        )
        as_other = client.get(
            "/docs", headers={"x-forwarded-user": "beta", "x-auth-provider": "oidc"}
        )

    assert "doc-restricted-list" in {item["id"] for item in as_creator.json()}
    assert "doc-restricted-list" not in {item["id"] for item in as_other.json()}


def test_list_hides_documents_with_no_access_metadata_row_when_adapter_is_real(tmp_path) -> None:
    """SEC-DOC-BOUND-06: absence of a document_access_metadata row defaults
    to Restricted for the list filter too, mirroring
    ServerOwnedDocumentResourceResolver's single-document default."""
    with _sqlite_client(tmp_path) as client:
        client.app.state.access_control_adapter = AllowAllAdapter()
        _provision(client, external_uid="alpha")
        _provision(client, external_uid="beta")

        put_resp = client.put(
            "/docs/doc-no-metadata-list",
            json=_sample_payload("doc-no-metadata-list"),
            headers={"x-forwarded-user": "alpha", "x-auth-provider": "oidc"},
        )
        assert put_resp.status_code == 200, put_resp.text
        # Deliberately no _insert_access_metadata call: no row at all.

        as_creator = client.get(
            "/docs", headers={"x-forwarded-user": "alpha", "x-auth-provider": "oidc"}
        )
        as_other = client.get(
            "/docs", headers={"x-forwarded-user": "beta", "x-auth-provider": "oidc"}
        )

    assert "doc-no-metadata-list" in {item["id"] for item in as_creator.json()}
    assert "doc-no-metadata-list" not in {item["id"] for item in as_other.json()}


def test_list_shows_public_and_org_documents_to_everyone_when_adapter_is_real(tmp_path) -> None:
    """SEC-DOC-BOUND-06: Public/Unlisted/Org need no ownership check -- Org's
    "visible within the tenant" is already satisfied by tenant scoping."""
    with _sqlite_client(tmp_path) as client:
        client.app.state.access_control_adapter = AllowAllAdapter()
        _provision(client, external_uid="alpha")
        _provision(client, external_uid="beta")

        for doc_id, visibility in (("doc-public-list", "Public"), ("doc-org-list", "Org")):
            put_resp = client.put(
                f"/docs/{doc_id}",
                json=_sample_payload(doc_id),
                headers={"x-forwarded-user": "alpha", "x-auth-provider": "oidc"},
            )
            assert put_resp.status_code == 200, put_resp.text
            _insert_access_metadata(tmp_path, doc_id=doc_id, visibility=visibility)

        as_other = client.get(
            "/docs", headers={"x-forwarded-user": "beta", "x-auth-provider": "oidc"}
        )

    other_ids = {item["id"] for item in as_other.json()}
    assert "doc-public-list" in other_ids
    assert "doc-org-list" in other_ids


def test_list_does_not_filter_by_visibility_when_adapter_is_noop_or_unset(tmp_path) -> None:
    """SEC-DOC-BOUND-06: the visibility filter must not activate when
    visibility is a no-op for single-document read/write too (no adapter, or
    the default noop adapter) -- otherwise the list would become *more*
    restrictive than GET/PUT /docs/{doc_id}, not more correct."""
    with _sqlite_client(tmp_path) as client:
        # Default app state: no override -- this is the NoopAccessControlAdapter,
        # not None, which is exactly the case this test guards.
        _provision(client, external_uid="alpha")
        _provision(client, external_uid="beta")

        put_resp = client.put(
            "/docs/doc-restricted-noop",
            json=_sample_payload("doc-restricted-noop"),
            headers={"x-forwarded-user": "alpha", "x-auth-provider": "oidc"},
        )
        assert put_resp.status_code == 200, put_resp.text
        _insert_access_metadata(tmp_path, doc_id="doc-restricted-noop", visibility="Restricted")

        as_other = client.get(
            "/docs", headers={"x-forwarded-user": "beta", "x-auth-provider": "oidc"}
        )

    assert "doc-restricted-noop" in {item["id"] for item in as_other.json()}


def test_server_derived_roles_from_provisioned_user(tmp_path) -> None:
    """SEC-AUTH-ATTRIB-01: roles set via admin provisioning are carried by the
    identity resolution (server-side), not read from client headers."""
    CapturingAdapter.last_request = None
    with _sqlite_client(tmp_path) as client:
        client.app.state.access_control_adapter = CapturingAdapter()

        # Provision a user with server-verified roles.
        provision = client.post(
            "/admin/provision/users",
            json={"provider": "oidc", "externalUid": "role-user", "displayName": "Role User", "roles": ["admin", "reviewer"]},
        )
        assert provision.status_code == 201, provision.text

        # Request as that user; the client-supplied roles header must be ignored,
        # and the provisioned roles must be present.
        resp = client.put(
            "/docs/doc-roles-prov",
            json=_sample_payload("doc-roles-prov"),
            headers={"x-forwarded-user": "role-user", "x-auth-provider": "oidc", "x-auth-roles": "superuser"},
        )
        assert resp.status_code == 200, resp.text

    captured_auth = CapturingAdapter.last_request.auth
    assert set(captured_auth.roles) == {"admin", "reviewer"}
