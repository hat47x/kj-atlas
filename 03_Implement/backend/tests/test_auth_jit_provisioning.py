from __future__ import annotations

from contextlib import contextmanager
from collections.abc import Iterator

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from kj_atlas_api.db import get_db
from kj_atlas_api.main import app
from kj_atlas_api.models import (
    Base,
    IdentityProviderRow,
    LOCAL_DEFAULT_TENANT_ID,
    TenantIdentityProviderRow,
    TenantMembershipRow,
    TenantRow,
    UserIdentityRow,
    UserRow,
)
from kj_atlas_api.settings import settings


@contextmanager
def _sqlite_client(
    tmp_path,
    *,
    allow_legacy_ambiguous_identities: bool = False,
) -> Iterator[tuple[TestClient, sessionmaker]]:
    db_path = tmp_path / "auth_jit.sqlite3"
    engine = create_engine(f"sqlite:///{db_path}")
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)
    if allow_legacy_ambiguous_identities:
        with engine.begin() as connection:
            connection.execute(text("DROP INDEX uq_user_identities_provider_lower_external_uid"))

    def _get_test_db():
        db = session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _get_test_db
    try:
        with TestClient(app) as client:
            yield client, session_local
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def _sample_payload(doc_id: str) -> dict:
    return {
        "version": 1,
        "id": doc_id,
        "title": "auth-jit-test",
        "createdAt": "2026-02-11T00:00:00Z",
        "updatedAt": "2026-02-11T00:00:00Z",
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
        "cards": [{"id": "card-1", "text": "alpha", "x": 0, "y": 0}],
        "edges": [],
        "islands": [],
    }


@pytest.mark.auth_level1
def test_jit_provisioning_creates_users_and_identities(tmp_path) -> None:
    original_allow_jit = settings.allow_jit_provisioning
    settings.allow_jit_provisioning = True
    try:
        with _sqlite_client(tmp_path) as fixture:
            client, session_local = fixture
            response = client.put(
                "/docs/doc-auth-jit",
                json=_sample_payload("doc-auth-jit"),
                headers={"x-forwarded-user": "alice", "x-auth-provider": "oidc"},
            )
            assert response.status_code == 200

            with session_local() as db:
                assert db.query(UserRow).count() == 1
                identity = db.query(UserIdentityRow).one()
                assert identity.provider == "oidc"
                assert identity.external_uid == "alice"
                assert identity.identity_provider_id is not None
                assert identity.subject == "alice"
                identity_provider = db.get(
                    IdentityProviderRow,
                    identity.identity_provider_id,
                )
                assert identity_provider is not None
                assert identity_provider.lifecycle_state == "active"
                assert (
                    db.get(
                        TenantIdentityProviderRow,
                        (LOCAL_DEFAULT_TENANT_ID, identity.identity_provider_id),
                    )
                    is not None
                )
                assert db.get(TenantRow, LOCAL_DEFAULT_TENANT_ID) is not None
                membership = db.query(TenantMembershipRow).one()
                assert membership.tenant_id == LOCAL_DEFAULT_TENANT_ID
                assert membership.user_id == identity.user_id
    finally:
        settings.allow_jit_provisioning = original_allow_jit


@pytest.mark.auth_level1
def test_strict_mode_requires_pre_provisioned_identity(tmp_path) -> None:
    original_allow_jit = settings.allow_jit_provisioning
    settings.allow_jit_provisioning = False
    try:
        with _sqlite_client(tmp_path) as fixture:
            client, session_local = fixture
            denied = client.put(
                "/docs/doc-auth-strict",
                json=_sample_payload("doc-auth-strict"),
                headers={"x-forwarded-user": "bob", "x-auth-provider": "saml"},
            )
            assert denied.status_code == 403
            assert denied.json()["detail"]["code"] == "identity_not_provisioned"
            assert (
                "Pre-provision via /admin/provision/users"
                in denied.json()["detail"]["message"]
            )

            provision = client.post(
                "/admin/provision/users",
                json={"provider": "saml", "externalUid": "bob", "displayName": "Bob"},
            )
            assert provision.status_code == 201
            assert provision.json()["provisioned"] is True

            retry = client.post(
                "/admin/provision/users",
                json={"provider": "saml", "externalUid": "bob", "displayName": "Bob"},
            )
            assert retry.status_code == 200
            assert retry.json()["provisioned"] is False

            conflict = client.post(
                "/admin/provision/users",
                json={
                    "provider": "saml",
                    "externalUid": "bob",
                    "displayName": "Not Bob",
                },
            )
            assert conflict.status_code == 409
            assert (
                conflict.json()["detail"]["code"]
                == "identity_already_provisioned_conflict"
            )
            assert (
                "conflicting profile attributes" in conflict.json()["detail"]["message"]
            )

            allowed = client.put(
                "/docs/doc-auth-strict",
                json=_sample_payload("doc-auth-strict"),
                headers={"x-forwarded-user": "bob", "x-auth-provider": "saml"},
            )
            assert allowed.status_code == 200

            with session_local() as db:
                membership = db.query(TenantMembershipRow).one()
                assert membership.tenant_id == LOCAL_DEFAULT_TENANT_ID
                assert membership.user_id == provision.json()["userId"]
    finally:
        settings.allow_jit_provisioning = original_allow_jit


@pytest.mark.auth_level1
def test_sso_subject_reviewer_ref_profile_on_provision(tmp_path) -> None:
    original_allow_jit = settings.allow_jit_provisioning
    original_adapter = settings.reviewer_ref_resolver_adapter
    settings.allow_jit_provisioning = False
    settings.reviewer_ref_resolver_adapter = "sso_subject"
    try:
        with _sqlite_client(tmp_path) as fixture:
            client, _ = fixture
            provision = client.post(
                "/admin/provision/users",
                json={
                    "provider": "oidc",
                    "externalUid": "sub-alice",
                    "displayName": "Alice",
                },
            )
            assert provision.status_code == 201
            payload = provision.json()
            assert payload["reviewerRef"] == "user:sso:oidc:sub-alice"
            assert payload["ownerRef"] == "user:sso:oidc:sub-alice"
    finally:
        settings.allow_jit_provisioning = original_allow_jit
        settings.reviewer_ref_resolver_adapter = original_adapter


@pytest.mark.auth_level1
def test_sso_subject_header_preferred_over_forwarded_user(tmp_path) -> None:
    original_allow_jit = settings.allow_jit_provisioning
    original_adapter = settings.reviewer_ref_resolver_adapter
    settings.allow_jit_provisioning = True
    settings.reviewer_ref_resolver_adapter = "sso_subject"
    try:
        with _sqlite_client(tmp_path) as fixture:
            client, _ = fixture
            provision = client.post(
                "/admin/provision/users",
                json={
                    "provider": "oidc",
                    "externalUid": "subject-header",
                    "displayName": "Alice",
                },
            )
            assert provision.status_code == 201

            response = client.put(
                "/docs/doc-auth-subject-priority",
                json=_sample_payload("doc-auth-subject-priority"),
                headers={
                    "x-auth-provider": "oidc",
                    "x-auth-subject": "subject-header",
                    "x-forwarded-user": "legacy-user-header",
                },
            )
            assert response.status_code == 200
    finally:
        settings.allow_jit_provisioning = original_allow_jit
        settings.reviewer_ref_resolver_adapter = original_adapter


def test_unauthenticated_path_keeps_actor_ref_fallback(tmp_path) -> None:
    original_allow_jit = settings.allow_jit_provisioning
    original_adapter = settings.reviewer_ref_resolver_adapter
    settings.allow_jit_provisioning = True
    settings.reviewer_ref_resolver_adapter = "sso_subject"
    try:
        with _sqlite_client(tmp_path) as fixture:
            client, _ = fixture
            response = client.put(
                "/docs/doc-auth-fallback",
                json=_sample_payload("doc-auth-fallback"),
                headers={"x-actor-ref": "actor:manual-reviewer"},
            )
            assert response.status_code == 200
    finally:
        settings.allow_jit_provisioning = original_allow_jit
        settings.reviewer_ref_resolver_adapter = original_adapter


@pytest.mark.auth_level1
def test_admin_provision_contract_rejects_extra_fields(tmp_path) -> None:
    original_allow_jit = settings.allow_jit_provisioning
    settings.allow_jit_provisioning = False
    try:
        with _sqlite_client(tmp_path) as fixture:
            client, _ = fixture
            response = client.post(
                "/admin/provision/users",
                json={
                    "provider": "oidc",
                    "externalUid": "extra-field-case",
                    "displayName": "Extra",
                    "unexpectedField": "not-allowed",
                },
            )
            assert response.status_code == 422
    finally:
        settings.allow_jit_provisioning = original_allow_jit


@pytest.mark.auth_level1
def test_admin_provision_contract_reviewer_and_owner_ref_prefix(tmp_path) -> None:
    original_allow_jit = settings.allow_jit_provisioning
    settings.allow_jit_provisioning = False
    try:
        with _sqlite_client(tmp_path) as fixture:
            client, _ = fixture
            response = client.post(
                "/admin/provision/users",
                json={
                    "provider": "oidc",
                    "externalUid": "prefix-check",
                    "displayName": "Prefix",
                },
            )
            assert response.status_code == 201
            payload = response.json()
            assert payload["reviewerRef"].startswith("user:")
            assert payload["ownerRef"].startswith("user:")
    finally:
        settings.allow_jit_provisioning = original_allow_jit


@pytest.mark.auth_level1
def test_admin_provision_contract_response_shape_is_stable_for_create_and_retry(
    tmp_path,
) -> None:
    original_allow_jit = settings.allow_jit_provisioning
    settings.allow_jit_provisioning = False
    try:
        with _sqlite_client(tmp_path) as fixture:
            client, _ = fixture
            create = client.post(
                "/admin/provision/users",
                json={
                    "provider": "oidc",
                    "externalUid": "shape-check",
                    "displayName": "Shape",
                },
            )
            assert create.status_code == 201
            created_payload = create.json()
            assert set(created_payload.keys()) == {
                "userId",
                "reviewerRef",
                "ownerRef",
                "provisioned",
            }
            assert isinstance(created_payload["userId"], str)
            assert isinstance(created_payload["reviewerRef"], str)
            assert isinstance(created_payload["ownerRef"], str)
            assert isinstance(created_payload["provisioned"], bool)
            assert created_payload["provisioned"] is True

            retry = client.post(
                "/admin/provision/users",
                json={
                    "provider": "oidc",
                    "externalUid": "shape-check",
                    "displayName": "Shape",
                },
            )
            assert retry.status_code == 200
            retried_payload = retry.json()
            assert set(retried_payload.keys()) == {
                "userId",
                "reviewerRef",
                "ownerRef",
                "provisioned",
            }
            assert retried_payload["userId"] == created_payload["userId"]
            assert retried_payload["provisioned"] is False
    finally:
        settings.allow_jit_provisioning = original_allow_jit


@pytest.mark.auth_level1
def test_admin_provision_normalizes_provider_case_for_idempotency(tmp_path) -> None:
    original_allow_jit = settings.allow_jit_provisioning
    settings.allow_jit_provisioning = False
    try:
        with _sqlite_client(tmp_path) as fixture:
            client, _ = fixture
            created = client.post(
                "/admin/provision/users",
                json={
                    "provider": "OIDC",
                    "externalUid": "provider-case",
                    "displayName": "Case",
                },
            )
            assert created.status_code == 201

            retry = client.post(
                "/admin/provision/users",
                json={
                    "provider": "oidc",
                    "externalUid": "provider-case",
                    "displayName": "Case",
                },
            )
            assert retry.status_code == 200
            assert retry.json()["provisioned"] is False
            assert retry.json()["userId"] == created.json()["userId"]
    finally:
        settings.allow_jit_provisioning = original_allow_jit


@pytest.mark.auth_level1
def test_docs_resolve_identity_accepts_provider_case_variant_under_strict_mode(
    tmp_path,
) -> None:
    original_allow_jit = settings.allow_jit_provisioning
    settings.allow_jit_provisioning = False
    try:
        with _sqlite_client(tmp_path) as fixture:
            client, _ = fixture
            provision = client.post(
                "/admin/provision/users",
                json={
                    "provider": "oidc",
                    "externalUid": "case-variant-sub",
                    "displayName": "Case",
                },
            )
            assert provision.status_code == 201

            response = client.put(
                "/docs/doc-auth-provider-case",
                json=_sample_payload("doc-auth-provider-case"),
                headers={
                    "x-forwarded-user": "case-variant-sub",
                    "x-auth-provider": "OIDC",
                },
            )
            assert response.status_code == 200
    finally:
        settings.allow_jit_provisioning = original_allow_jit


@pytest.mark.auth_level1
def test_admin_provision_rejects_ambiguous_identity_mapping(tmp_path) -> None:
    original_allow_jit = settings.allow_jit_provisioning
    settings.allow_jit_provisioning = False
    try:
        with _sqlite_client(tmp_path, allow_legacy_ambiguous_identities=True) as fixture:
            client, session_local = fixture
            with session_local() as db:
                user_1 = UserRow(
                    id="user-ambiguous-1",
                    display_name="Ambiguous One",
                    email=None,
                    lifecycle_state="active",
                    created_at="2026-03-14T00:00:00Z",
                    updated_at="2026-03-14T00:00:00Z",
                )
                user_2 = UserRow(
                    id="user-ambiguous-2",
                    display_name="Ambiguous Two",
                    email=None,
                    lifecycle_state="active",
                    created_at="2026-03-14T00:00:00Z",
                    updated_at="2026-03-14T00:00:00Z",
                )
                db.add_all([user_1, user_2])
                db.add_all(
                    [
                        UserIdentityRow(
                            user_id=user_1.id,
                            provider="oidc",
                            external_uid="ambiguous-sub",
                            created_at="2026-03-14T00:00:00Z",
                        ),
                        UserIdentityRow(
                            user_id=user_2.id,
                            provider="OIDC",
                            external_uid="ambiguous-sub",
                            created_at="2026-03-14T00:00:00Z",
                        ),
                    ]
                )
                db.commit()

            response = client.post(
                "/admin/provision/users",
                json={
                    "provider": "oidc",
                    "externalUid": "ambiguous-sub",
                    "displayName": "Ambiguous",
                },
            )
            assert response.status_code == 409
            payload = response.json()
            assert payload["detail"]["code"] == "identity_mapping_conflict"
    finally:
        settings.allow_jit_provisioning = original_allow_jit


@pytest.mark.auth_level1
def test_docs_strict_mode_rejects_ambiguous_identity_mapping(tmp_path) -> None:
    original_allow_jit = settings.allow_jit_provisioning
    settings.allow_jit_provisioning = False
    try:
        with _sqlite_client(tmp_path, allow_legacy_ambiguous_identities=True) as fixture:
            client, session_local = fixture
            with session_local() as db:
                user_1 = UserRow(
                    id="user-doc-ambiguous-1",
                    display_name="Doc Ambiguous One",
                    email=None,
                    lifecycle_state="active",
                    created_at="2026-03-14T00:00:00Z",
                    updated_at="2026-03-14T00:00:00Z",
                )
                user_2 = UserRow(
                    id="user-doc-ambiguous-2",
                    display_name="Doc Ambiguous Two",
                    email=None,
                    lifecycle_state="active",
                    created_at="2026-03-14T00:00:00Z",
                    updated_at="2026-03-14T00:00:00Z",
                )
                db.add_all([user_1, user_2])
                db.add_all(
                    [
                        UserIdentityRow(
                            user_id=user_1.id,
                            provider="saml",
                            external_uid="ambiguous-strict",
                            created_at="2026-03-14T00:00:00Z",
                        ),
                        UserIdentityRow(
                            user_id=user_2.id,
                            provider="SAML",
                            external_uid="ambiguous-strict",
                            created_at="2026-03-14T00:00:00Z",
                        ),
                    ]
                )
                db.commit()

            response = client.put(
                "/docs/doc-auth-ambiguous-strict",
                json=_sample_payload("doc-auth-ambiguous-strict"),
                headers={"x-forwarded-user": "ambiguous-strict", "x-auth-provider": "saml"},
            )
            assert response.status_code == 409
            payload = response.json()
            assert payload["detail"]["code"] == "identity_mapping_conflict"
    finally:
        settings.allow_jit_provisioning = original_allow_jit


@pytest.mark.auth_level1
def test_strict_mode_accepts_provider_case_and_whitespace_variants(tmp_path) -> None:
    original_allow_jit = settings.allow_jit_provisioning
    settings.allow_jit_provisioning = False
    try:
        with _sqlite_client(tmp_path) as fixture:
            client, _ = fixture
            provision = client.post(
                "/admin/provision/users",
                json={
                    "provider": "  OIDC  ",
                    "externalUid": "case-variant-user",
                    "displayName": "Case Variant",
                },
            )
            assert provision.status_code == 201

            allowed = client.put(
                "/docs/doc-auth-case-variant",
                json=_sample_payload("doc-auth-case-variant"),
                headers={"x-forwarded-user": "case-variant-user", "x-auth-provider": "oidc"},
            )
            assert allowed.status_code == 200
    finally:
        settings.allow_jit_provisioning = original_allow_jit


@pytest.mark.auth_level1
def test_admin_provision_contract_rejects_blank_provider_or_external_uid(tmp_path) -> None:
    original_allow_jit = settings.allow_jit_provisioning
    settings.allow_jit_provisioning = False
    try:
        with _sqlite_client(tmp_path) as fixture:
            client, _ = fixture
            blank_provider = client.post(
                "/admin/provision/users",
                json={"provider": "   ", "externalUid": "user-a", "displayName": "A"},
            )
            # SEC-HTTP-01: blank required field is a domain contract violation (422).
            assert blank_provider.status_code == 422

            blank_external_uid = client.post(
                "/admin/provision/users",
                json={"provider": "oidc", "externalUid": "   ", "displayName": "B"},
            )
            assert blank_external_uid.status_code == 422
    finally:
        settings.allow_jit_provisioning = original_allow_jit


@pytest.mark.auth_level1
@pytest.mark.parametrize(
    ("runtime_profile", "expected_status", "expected_code"),
    [
        # ADR-0072 D2=A: the control plane is no longer refused by profile. It is
        # reachable on SaaS and protected by authorization instead, so an
        # unauthorized caller gets 401 rather than the former 404
        # "strict_provisioning_unavailable". The old behaviour made SaaS
        # bootstrap impossible: IdP registration was the one thing that had to
        # happen before authentication could work, and it 404'd on that profile
        # while the startup warning told the operator to call it
        # (SEC-ADMIN-PLANE-01 課題2).
        ("saas-multitenant", 401, "control_plane_unauthorized"),
        # An unknown profile still refuses outright: it must not fall through to
        # the unconfigured-and-open branch.
        ("unknown", 503, "runtime_policy_unavailable"),
    ],
)
def test_strict_provisioning_outside_single_tenant_refuses_before_touching_the_database(
    tmp_path,
    runtime_profile: str,
    expected_status: int,
    expected_code: str,
) -> None:
    with _sqlite_client(tmp_path) as fixture:
        client, session_local = fixture
        client.app.state.runtime_profile = runtime_profile

        response = client.post(
            "/admin/provision/users",
            json={"provider": "oidc", "externalUid": "blocked-user"},
        )

        assert response.status_code == expected_status
        assert response.json()["detail"]["code"] == expected_code
        with session_local() as db:
            assert db.query(UserRow).count() == 0
            assert db.query(UserIdentityRow).count() == 0
            assert db.query(TenantMembershipRow).count() == 0


@pytest.mark.auth_level1
def test_suspended_membership_blocks_document_access(tmp_path) -> None:
    original_allow_jit = settings.allow_jit_provisioning
    settings.allow_jit_provisioning = False
    try:
        with _sqlite_client(tmp_path) as fixture:
            client, session_local = fixture
            provision = client.post(
                "/admin/provision/users",
                json={
                    "provider": "oidc",
                    "externalUid": "suspended-member",
                    "displayName": "Suspended",
                },
            )
            assert provision.status_code == 201

            headers = {
                "x-auth-provider": "oidc",
                "x-auth-subject": "suspended-member",
                "x-tenant-id": "untrusted-tenant-input",
            }
            allowed = client.put(
                "/docs/doc-membership-state",
                json=_sample_payload("doc-membership-state"),
                headers=headers,
            )
            assert allowed.status_code == 200

            with session_local() as db:
                membership = db.get(
                    TenantMembershipRow,
                    (LOCAL_DEFAULT_TENANT_ID, provision.json()["userId"]),
                )
                assert membership is not None
                membership.lifecycle_state = "suspended"
                db.commit()

            denied = client.get("/docs/doc-membership-state", headers=headers)
            assert denied.status_code == 403
            assert denied.json()["detail"]["code"] == "tenant_membership_inactive"
    finally:
        settings.allow_jit_provisioning = original_allow_jit


@pytest.mark.auth_level1
def test_identity_lookup_prefers_identity_provider_subject_binding(tmp_path) -> None:
    original_allow_jit = settings.allow_jit_provisioning
    settings.allow_jit_provisioning = False
    try:
        with _sqlite_client(tmp_path) as fixture:
            client, session_local = fixture
            created = client.post(
                "/admin/provision/users",
                json={
                    "provider": "oidc",
                    "externalUid": "structured-subject",
                    "displayName": "Structured",
                },
            )
            assert created.status_code == 201

            with session_local() as db:
                identity = db.query(UserIdentityRow).one()
                identity.provider = "retired-legacy-label"
                identity.external_uid = "retired-legacy-subject"
                db.commit()

            resolved = client.post(
                "/admin/provision/users",
                json={
                    "provider": "oidc",
                    "externalUid": "structured-subject",
                    "displayName": "Structured",
                },
            )
            assert resolved.status_code == 200
            assert resolved.json()["userId"] == created.json()["userId"]
            assert resolved.json()["provisioned"] is False
    finally:
        settings.allow_jit_provisioning = original_allow_jit


@pytest.mark.auth_level1
def test_legacy_identity_lookup_self_heals_expand_binding(tmp_path) -> None:
    original_allow_jit = settings.allow_jit_provisioning
    settings.allow_jit_provisioning = False
    try:
        with _sqlite_client(tmp_path) as fixture:
            client, session_local = fixture
            with session_local() as db:
                db.add(
                    UserRow(
                        id="legacy-user",
                        display_name="Legacy",
                        email=None,
                        lifecycle_state="active",
                        created_at="2026-07-17T00:00:00Z",
                        updated_at="2026-07-17T00:00:00Z",
                    )
                )
                db.add(
                    UserIdentityRow(
                        user_id="legacy-user",
                        provider="oidc",
                        external_uid="legacy-subject",
                        identity_provider_id=None,
                        subject=None,
                        created_at="2026-07-17T00:00:00Z",
                    )
                )
                db.commit()

            resolved = client.post(
                "/admin/provision/users",
                json={
                    "provider": "oidc",
                    "externalUid": "legacy-subject",
                    "displayName": "Legacy",
                },
            )
            assert resolved.status_code == 200
            assert resolved.json()["userId"] == "legacy-user"

            with session_local() as db:
                identity = db.query(UserIdentityRow).one()
                assert identity.identity_provider_id is not None
                assert identity.subject == "legacy-subject"
                membership = db.get(
                    TenantMembershipRow,
                    (LOCAL_DEFAULT_TENANT_ID, "legacy-user"),
                )
                assert membership is not None
    finally:
        settings.allow_jit_provisioning = original_allow_jit
