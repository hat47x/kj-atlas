from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import Session, sessionmaker

import kj_atlas_api.guest_redeem as guest_redeem_module
from kj_atlas_api.db import get_db
from kj_atlas_api.guest_admission_models import GuestDocumentGrantRow, GuestPrincipalRow
from kj_atlas_api.guest_auth_session_models import GuestAuthSessionRow
from kj_atlas_api.guest_auth_state import DatabaseGuestAuthSessionStore
from kj_atlas_api.guest_redeem import (
    DatabaseGuestRedeemStateStore,
    GuestIdentityVerificationError,
    VerifiedGuestIdentity,
)
from kj_atlas_api.guest_redeem_state_models import GuestRedeemStateRow
from kj_atlas_api.models import (
    Base,
    DocumentRow,
    TenantIdentityProviderRow,
    TenantMembershipRow,
    TenantRow,
)
from kj_atlas_api.routes.docs import router as docs_router
from kj_atlas_api.routes.guest_session import router as guest_session_router

NOW = datetime(2026, 9, 7, 0, 30, tzinfo=timezone.utc)
TS = NOW.isoformat()
STATE_HASH_KEY = b"guest-redeem-state-test-key-012345"
SESSION_HASH_KEY = b"guest-session-test-key-01234567890"
ISSUER = "https://personal-idp.example.test"
SUBJECT = "personal-subject-1"


def _payload(doc_id: str) -> dict[str, object]:
    return {
        "version": 1,
        "id": doc_id,
        "title": doc_id,
        "createdAt": "2026-09-07T00:30:00Z",
        "updatedAt": "2026-09-07T00:30:00Z",
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
        "cards": [],
        "edges": [],
        "islands": [],
    }


class AcceptingVerifier:
    def verify_identity(self, *, credential: str, verification_method: str) -> VerifiedGuestIdentity:
        assert credential == "provider-proof"
        assert verification_method == "personal_account"
        return VerifiedGuestIdentity(issuer=ISSUER, subject=SUBJECT)


class RejectingVerifier:
    def verify_identity(self, *, credential: str, verification_method: str) -> VerifiedGuestIdentity:
        raise GuestIdentityVerificationError("provider rejected credential")


@pytest.fixture
def redeem_env(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path}/guest-redeem.db")
    factory = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)
    Base.metadata.create_all(engine)
    with factory() as db:
        db.add(
            TenantRow(
                id="tenant-a",
                display_name="Tenant A",
                lifecycle_state="active",
                created_at=TS,
                updated_at=TS,
            )
        )
        db.add(
            DocumentRow(
                tenant_id="tenant-a",
                id="doc-granted",
                version=1,
                updated_at=TS,
                payload_json=json.dumps(_payload("doc-granted")),
                created_by="owner-1",
                lifecycle_state="active",
            )
        )
        db.add(
            GuestPrincipalRow(
                tenant_id="tenant-a",
                guest_principal_id="guest-1",
                invited_email="guest@example.test",
                status="pending",
                verification_method="personal_account",
                verified_issuer=None,
                verified_subject=None,
                created_by="owner-1",
                created_at=TS,
                expires_at=(NOW + timedelta(hours=2)).isoformat(),
                redeemed_at=None,
                revoked_at=None,
            )
        )
        db.add(
            GuestDocumentGrantRow(
                tenant_id="tenant-a",
                guest_principal_id="guest-1",
                doc_id="doc-granted",
                granted_by="owner-1",
                granted_at=TS,
                revoked_at=None,
            )
        )
        db.commit()

    state_store = DatabaseGuestRedeemStateStore(factory)
    auth_store = DatabaseGuestAuthSessionStore(factory)
    raw_state = state_store.issue_redeem_state(
        tenant_id="tenant-a",
        guest_principal_id="guest-1",
        hash_key=STATE_HASH_KEY,
        now=NOW,
    )

    def make_client(verifier=AcceptingVerifier()):
        app = FastAPI()
        app.include_router(guest_session_router)
        app.include_router(docs_router)
        app.state.runtime_profile = "evaluation"
        app.state.guest_redeem_state_store = state_store
        app.state.guest_redeem_state_hash_key = STATE_HASH_KEY
        app.state.guest_identity_verifier = verifier
        app.state.guest_auth_session_store = auth_store
        app.state.guest_auth_session_hash_key = SESSION_HASH_KEY
        app.state.access_control_adapter = None
        app.state.audit_dispatcher = None

        def _test_db():
            with factory() as db:
                yield db

        app.dependency_overrides[get_db] = _test_db
        return TestClient(app)

    yield factory, state_store, raw_state, make_client
    engine.dispose()


def _redeem(client: TestClient, raw_state: str, **extra):
    payload = {"state": raw_state, "identityCredential": "provider-proof", **extra}
    return client.post("/session/guest/redeem", json=payload)


def test_redeem_uses_host_state_then_existing_exact_grant(redeem_env) -> None:
    factory, _, raw_state, make_client = redeem_env
    with factory() as db:
        stored = db.scalar(select(GuestRedeemStateRow))
        assert stored is not None
        assert raw_state not in stored.state_key_hash

    with make_client() as client:
        response = _redeem(client, raw_state)
        assert response.status_code == 200
        assert response.json() == {"status": "redeemed"}
        assert "Kj-Atlas-Guest-Session" in response.cookies
        read = client.get(
            "/docs/doc-granted",
            cookies={
                "Kj-Atlas-Guest-Session": response.cookies["Kj-Atlas-Guest-Session"]
            },
        )
        assert read.status_code == 200
        assert read.json()["id"] == "doc-granted"

    with factory() as db:
        principal = db.get(GuestPrincipalRow, ("tenant-a", "guest-1"))
        assert principal is not None
        assert principal.status == "active"
        assert principal.verified_issuer == ISSUER
        assert principal.verified_subject == SUBJECT
        assert db.scalars(select(TenantMembershipRow)).all() == []
        assert db.scalars(select(TenantIdentityProviderRow)).all() == []
        assert len(db.scalars(select(GuestAuthSessionRow)).all()) == 1
        state = db.scalar(select(GuestRedeemStateRow))
        assert state is not None and state.consumed_at is not None


def test_redeem_state_is_one_time(redeem_env) -> None:
    _, _, raw_state, make_client = redeem_env
    with make_client() as client:
        assert _redeem(client, raw_state).status_code == 200
        replay = _redeem(client, raw_state)
    assert replay.status_code == 401
    assert replay.json()["detail"]["code"] == "guest_redeem_invalid"


def test_client_cannot_supply_tenant_principal_or_identity_claims(redeem_env) -> None:
    factory, _, raw_state, make_client = redeem_env
    with make_client() as client:
        response = _redeem(
            client,
            raw_state,
            tenantId="tenant-b",
            guestPrincipalId="attacker",
            issuer="https://attacker.invalid",
            subject="attacker",
        )
    assert response.status_code == 422
    with factory() as db:
        principal = db.get(GuestPrincipalRow, ("tenant-a", "guest-1"))
        state = db.scalar(select(GuestRedeemStateRow))
        assert principal is not None and principal.status == "pending"
        assert state is not None and state.consumed_at is None


def test_identity_verification_failure_does_not_consume_or_activate(redeem_env) -> None:
    factory, _, raw_state, make_client = redeem_env
    with make_client(RejectingVerifier()) as client:
        response = _redeem(client, raw_state)
    assert response.status_code == 401
    with factory() as db:
        principal = db.get(GuestPrincipalRow, ("tenant-a", "guest-1"))
        state = db.scalar(select(GuestRedeemStateRow))
        assert principal is not None and principal.status == "pending"
        assert state is not None and state.consumed_at is None
        assert db.scalars(select(GuestAuthSessionRow)).all() == []


def test_session_persistence_failure_rolls_back_activation_and_state(redeem_env, monkeypatch) -> None:
    factory, _, raw_state, make_client = redeem_env

    def fail_session(*args, **kwargs):
        raise RuntimeError("forced session persistence failure")

    monkeypatch.setattr(
        guest_redeem_module,
        "create_guest_auth_session_in_transaction",
        fail_session,
    )
    with make_client() as client:
        response = _redeem(client, raw_state)
    assert response.status_code == 503
    with factory() as db:
        principal = db.get(GuestPrincipalRow, ("tenant-a", "guest-1"))
        state = db.scalar(select(GuestRedeemStateRow))
        assert principal is not None and principal.status == "pending"
        assert principal.verified_issuer is None
        assert state is not None and state.consumed_at is None
        assert db.scalars(select(GuestAuthSessionRow)).all() == []


def test_expired_state_fails_closed(redeem_env) -> None:
    factory, _, raw_state, make_client = redeem_env
    with factory() as db:
        db.execute(
            update(GuestRedeemStateRow).values(
                expires_at=(datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
            )
        )
        db.commit()
    with make_client() as client:
        response = _redeem(client, raw_state)
    assert response.status_code == 401
