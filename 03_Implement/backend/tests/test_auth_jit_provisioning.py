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

            allowed = client.put(
                "/docs/doc-auth-strict",
                json=_sample_payload("doc-auth-strict"),
                headers={"x-forwarded-user": "bob", "x-auth-provider": "saml"},
            )
            assert allowed.status_code == 200
    finally:
        settings.allow_jit_provisioning = original_allow_jit
