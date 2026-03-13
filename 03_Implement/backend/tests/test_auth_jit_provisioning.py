from __future__ import annotations

from contextlib import contextmanager
from collections.abc import Iterator

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from kj_atlas_api.db import get_db
from kj_atlas_api.main import app
from kj_atlas_api.models import Base, UserIdentityRow, UserRow
from kj_atlas_api.settings import settings


@contextmanager
def _sqlite_client(tmp_path) -> Iterator[tuple[TestClient, sessionmaker]]:
    db_path = tmp_path / "auth_jit.sqlite3"
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
    finally:
        settings.allow_jit_provisioning = original_allow_jit


@pytest.mark.auth_level1
def test_strict_mode_requires_pre_provisioned_identity(tmp_path) -> None:
    original_allow_jit = settings.allow_jit_provisioning
    settings.allow_jit_provisioning = False
    try:
        with _sqlite_client(tmp_path) as fixture:
            client, _ = fixture
            denied = client.put(
                "/docs/doc-auth-strict",
                json=_sample_payload("doc-auth-strict"),
                headers={"x-forwarded-user": "bob", "x-auth-provider": "saml"},
            )
            assert denied.status_code == 403
            assert denied.json()["detail"]["code"] == "identity_not_provisioned"
            assert "Pre-provision via /admin/provision/users" in denied.json()["detail"]["message"]

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
                json={"provider": "saml", "externalUid": "bob", "displayName": "Not Bob"},
            )
            assert conflict.status_code == 409
            assert conflict.json()["detail"]["code"] == "identity_already_provisioned_conflict"
            assert "conflicting profile attributes" in conflict.json()["detail"]["message"]

            allowed = client.put(
                "/docs/doc-auth-strict",
                json=_sample_payload("doc-auth-strict"),
                headers={"x-forwarded-user": "bob", "x-auth-provider": "saml"},
            )
            assert allowed.status_code == 200
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
                json={"provider": "oidc", "externalUid": "sub-alice", "displayName": "Alice"},
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
                json={"provider": "oidc", "externalUid": "subject-header", "displayName": "Alice"},
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
                json={"provider": "oidc", "externalUid": "prefix-check", "displayName": "Prefix"},
            )
            assert response.status_code == 201
            payload = response.json()
            assert payload["reviewerRef"].startswith("user:")
            assert payload["ownerRef"].startswith("user:")
    finally:
        settings.allow_jit_provisioning = original_allow_jit


@pytest.mark.auth_level1
def test_admin_provision_contract_response_shape_is_stable_for_create_and_retry(tmp_path) -> None:
    original_allow_jit = settings.allow_jit_provisioning
    settings.allow_jit_provisioning = False
    try:
        with _sqlite_client(tmp_path) as fixture:
            client, _ = fixture
            create = client.post(
                "/admin/provision/users",
                json={"provider": "oidc", "externalUid": "shape-check", "displayName": "Shape"},
            )
            assert create.status_code == 201
            created_payload = create.json()
            assert set(created_payload.keys()) == {"userId", "reviewerRef", "ownerRef", "provisioned"}
            assert isinstance(created_payload["userId"], str)
            assert isinstance(created_payload["reviewerRef"], str)
            assert isinstance(created_payload["ownerRef"], str)
            assert isinstance(created_payload["provisioned"], bool)
            assert created_payload["provisioned"] is True

            retry = client.post(
                "/admin/provision/users",
                json={"provider": "oidc", "externalUid": "shape-check", "displayName": "Shape"},
            )
            assert retry.status_code == 200
            retried_payload = retry.json()
            assert set(retried_payload.keys()) == {"userId", "reviewerRef", "ownerRef", "provisioned"}
            assert retried_payload["userId"] == created_payload["userId"]
            assert retried_payload["provisioned"] is False
    finally:
        settings.allow_jit_provisioning = original_allow_jit
