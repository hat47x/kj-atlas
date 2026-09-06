from __future__ import annotations

import json
from collections.abc import Iterator
from datetime import datetime, timezone

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from kj_atlas_api.db import get_db
from kj_atlas_api.guest_admission_models import GuestDocumentGrantRow, GuestPrincipalRow
from kj_atlas_api.guest_admission_repository import GuestAdmissionRepository
from kj_atlas_api.guest_auth_session_models import GuestAuthSessionRow  # noqa: F401
from kj_atlas_api.guest_auth_state import DatabaseGuestAuthSessionStore
from kj_atlas_api.guest_request_auth import GUEST_AUTH_SESSION_COOKIE, issue_guest_auth_session
from kj_atlas_api.models import Base, DocumentRow, TenantMembershipRow, TenantRow
from kj_atlas_api.routes.docs import router as docs_router

TIMESTAMP = "2026-09-06T00:00:00+00:00"
HASH_KEY = b"guest-http-test-key-01234567890123"
ISSUER = "https://guest-idp.invalid"
SUBJECT = "guest-subject-1"


def _payload(doc_id: str) -> dict[str, object]:
    return {
        "version": 1,
        "id": doc_id,
        "title": doc_id,
        "createdAt": "2026-09-06T00:00:00Z",
        "updatedAt": "2026-09-06T00:00:00Z",
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
        "cards": [],
        "edges": [],
        "islands": [],
    }


@pytest.fixture
def guest_client(tmp_path) -> Iterator[tuple[TestClient, sessionmaker[Session], str]]:
    engine = create_engine(f"sqlite:///{tmp_path}/guest-http.db")
    factory = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)
    Base.metadata.create_all(engine)
    with factory() as db:
        db.add_all(
            [
                TenantRow(
                    id="tenant-a",
                    display_name="Tenant A",
                    lifecycle_state="active",
                    created_at=TIMESTAMP,
                    updated_at=TIMESTAMP,
                ),
                TenantRow(
                    id="tenant-b",
                    display_name="Tenant B",
                    lifecycle_state="active",
                    created_at=TIMESTAMP,
                    updated_at=TIMESTAMP,
                ),
                DocumentRow(
                    tenant_id="tenant-a",
                    id="doc-granted",
                    version=1,
                    updated_at=TIMESTAMP,
                    payload_json=json.dumps(_payload("doc-granted")),
                    created_by="owner-1",
                    lifecycle_state="active",
                ),
                DocumentRow(
                    tenant_id="tenant-a",
                    id="doc-ungranted",
                    version=1,
                    updated_at=TIMESTAMP,
                    payload_json=json.dumps(_payload("doc-ungranted")),
                    created_by="owner-1",
                    lifecycle_state="active",
                ),
                DocumentRow(
                    tenant_id="tenant-b",
                    id="doc-other-tenant",
                    version=1,
                    updated_at=TIMESTAMP,
                    payload_json=json.dumps(_payload("doc-other-tenant")),
                    created_by="owner-2",
                    lifecycle_state="active",
                ),
                GuestPrincipalRow(
                    tenant_id="tenant-a",
                    guest_principal_id="guest-1",
                    invited_email="guest@example.invalid",
                    status="active",
                    verification_method="personal_account",
                    verified_issuer=ISSUER,
                    verified_subject=SUBJECT,
                    created_by="owner-1",
                    created_at=TIMESTAMP,
                    expires_at="2026-09-07T00:00:00+00:00",
                    redeemed_at=TIMESTAMP,
                    revoked_at=None,
                ),
                GuestDocumentGrantRow(
                    tenant_id="tenant-a",
                    guest_principal_id="guest-1",
                    doc_id="doc-granted",
                    granted_by="owner-1",
                    granted_at=TIMESTAMP,
                    revoked_at=None,
                ),
            ]
        )
        db.commit()

    store = DatabaseGuestAuthSessionStore(factory)
    raw_session = issue_guest_auth_session(
        store=store,
        hash_key=HASH_KEY,
        tenant_id="tenant-a",
        guest_principal_id="guest-1",
        issuer=ISSUER,
        subject=SUBJECT,
    )

    app = FastAPI()
    app.include_router(docs_router)
    app.state.guest_auth_session_store = store
    app.state.guest_auth_session_hash_key = HASH_KEY
    app.state.access_control_adapter = None
    app.state.audit_dispatcher = None

    def _test_db():
        with factory() as db:
            yield db

    app.dependency_overrides[get_db] = _test_db
    with TestClient(app) as client:
        yield client, factory, raw_session
    engine.dispose()


def _cookies(raw_session: str) -> dict[str, str]:
    return {GUEST_AUTH_SESSION_COOKIE: raw_session}


def test_guest_exact_grant_reads_document_without_membership(guest_client) -> None:
    client, factory, raw_session = guest_client

    response = client.get("/docs/doc-granted", cookies=_cookies(raw_session))

    assert response.status_code == 200
    assert response.json()["id"] == "doc-granted"
    with factory() as db:
        assert db.scalars(select(TenantMembershipRow)).all() == []


def test_guest_principal_does_not_imply_same_tenant_visibility(guest_client) -> None:
    client, _, raw_session = guest_client

    response = client.get("/docs/doc-ungranted", cookies=_cookies(raw_session))

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "guest_document_not_granted"


def test_guest_cannot_cross_tenant_boundary(guest_client) -> None:
    client, _, raw_session = guest_client

    response = client.get("/docs/doc-other-tenant", cookies=_cookies(raw_session))

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "guest_document_not_granted"


def test_grant_revoke_denies_the_next_http_request_with_same_live_cookie(guest_client) -> None:
    client, factory, raw_session = guest_client
    with factory() as db:
        repo = GuestAdmissionRepository(db, tenant_id="tenant-a")
        assert repo.revoke_document_grant(
            guest_principal_id="guest-1",
            doc_id="doc-granted",
            revoked_at=datetime.now(timezone.utc).isoformat(),
        )
        db.commit()

    response = client.get("/docs/doc-granted", cookies=_cookies(raw_session))

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "guest_document_not_granted"


def test_principal_revoke_invalidates_the_next_http_request_with_same_cookie(guest_client) -> None:
    client, factory, raw_session = guest_client
    with factory() as db:
        repo = GuestAdmissionRepository(db, tenant_id="tenant-a")
        assert repo.revoke_guest_principal(
            guest_principal_id="guest-1",
            revoked_at=datetime.now(timezone.utc).isoformat(),
        )
        db.commit()

    response = client.get("/docs/doc-granted", cookies=_cookies(raw_session))

    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "guest_session_invalid"


def test_guest_write_is_explicitly_denied_in_r2a(guest_client) -> None:
    client, _, raw_session = guest_client

    response = client.put(
        "/docs/doc-granted",
        cookies=_cookies(raw_session),
        json=_payload("doc-granted"),
    )

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "guest_write_not_enabled"
