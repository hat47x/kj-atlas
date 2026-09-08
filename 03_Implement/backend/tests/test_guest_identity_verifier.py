from __future__ import annotations

import base64
import json
import time
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from kj_atlas_api.db import get_db
from kj_atlas_api.guest_admission_models import GuestDocumentGrantRow, GuestPrincipalRow
from kj_atlas_api.guest_admission_repository import GuestAdmissionRepository
from kj_atlas_api.guest_auth_state import DatabaseGuestAuthSessionStore
from kj_atlas_api.guest_identity_verifier import DatabaseJwtGuestIdentityVerifier
from kj_atlas_api.guest_redeem import (
    DatabaseGuestRedeemStateStore,
    GuestIdentityVerificationError,
    GuestIdentityVerificationUnavailableError,
)
from kj_atlas_api.jwks_store import JwksStore
from kj_atlas_api.models import (
    Base,
    DocumentRow,
    IdentityProviderRow,
    TenantIdentityProviderRow,
    TenantMembershipRow,
    TenantRow,
    UserIdentityRow,
)
from kj_atlas_api.routes.docs import router as docs_router
from kj_atlas_api.routes.guest_session import router as guest_session_router

NOW = datetime.now(timezone.utc).replace(microsecond=0)
TS = NOW.isoformat()
ISSUER = "https://personal-idp.example.test"
AUDIENCE = "kj-atlas-guest"
STATE_HASH_KEY = b"guest-r2c-state-hash-key-0123456789"
SESSION_HASH_KEY = b"guest-r2c-session-hash-key-0123456"


def _b64url(value: int) -> str:
    length = (value.bit_length() + 7) // 8
    return base64.urlsafe_b64encode(value.to_bytes(length, "big")).rstrip(b"=").decode()


def _key_pair() -> tuple[rsa.RSAPrivateKey, dict[str, object]]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    numbers = private_key.public_key().public_numbers()
    return private_key, {
        "kty": "RSA",
        "kid": "guest-r2c-key",
        "use": "sig",
        "alg": "RS256",
        "n": _b64url(numbers.n),
        "e": _b64url(numbers.e),
    }


def _pem(private_key: rsa.RSAPrivateKey) -> str:
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()


def _token(
    private_key: rsa.RSAPrivateKey,
    *,
    issuer: str = ISSUER,
    audience: str = AUDIENCE,
    subject: str = "guest-subject-1",
) -> str:
    now = int(time.time())
    return jwt.encode(
        {
            "iss": issuer,
            "aud": audience,
            "sub": subject,
            "iat": now - 5,
            "exp": now + 3600,
        },
        _pem(private_key),
        algorithm="RS256",
        headers={"kid": "guest-r2c-key"},
    )


def _payload(doc_id: str) -> dict[str, object]:
    return {
        "version": 1,
        "id": doc_id,
        "title": doc_id,
        "createdAt": TS,
        "updatedAt": TS,
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
        "cards": [],
        "edges": [],
        "islands": [],
    }


@pytest.fixture
def guest_env(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path}/guest-r2c.db")
    factory = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)
    Base.metadata.create_all(engine)
    private_key, jwk = _key_pair()

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
            IdentityProviderRow(
                id="guest-idp",
                issuer=ISSUER,
                audience=AUDIENCE,
                protocol="oidc",
                jwks_uri="https://personal-idp.example.test/.well-known/jwks.json",
                lifecycle_state="active",
                created_at=TS,
                updated_at=TS,
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

    jwks = JwksStore()
    jwks.set("guest-idp", [jwk])
    verifier = DatabaseJwtGuestIdentityVerifier(
        session_factory=factory,
        jwks_store=jwks,
    )
    redeem_store = DatabaseGuestRedeemStateStore(factory)
    auth_store = DatabaseGuestAuthSessionStore(factory)
    raw_state = redeem_store.issue_redeem_state(
        tenant_id="tenant-a",
        guest_principal_id="guest-1",
        hash_key=STATE_HASH_KEY,
        now=NOW,
    )

    app = FastAPI()
    app.include_router(guest_session_router)
    app.include_router(docs_router)
    app.state.runtime_profile = "evaluation"
    app.state.guest_redeem_state_store = redeem_store
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
    yield factory, private_key, jwk, verifier, raw_state, TestClient(app)
    engine.dispose()


def _redeem(client: TestClient, raw_state: str, token: str):
    return client.post(
        "/session/guest/redeem",
        json={"state": raw_state, "identityCredential": token},
    )


def _guest_cookie(response) -> dict[str, str]:
    return {"Kj-Atlas-Guest-Session": response.cookies["Kj-Atlas-Guest-Session"]}


def test_real_signed_guest_token_redeems_without_member_or_tenant_idp_trust(guest_env) -> None:
    factory, private_key, _, _, raw_state, client = guest_env
    with client:
        response = _redeem(client, raw_state, _token(private_key))
        assert response.status_code == 200
        read = client.get("/docs/doc-granted", cookies=_guest_cookie(response))
        assert read.status_code == 200

    with factory() as db:
        principal = db.get(GuestPrincipalRow, ("tenant-a", "guest-1"))
        assert principal is not None
        assert principal.status == "active"
        assert principal.verified_issuer == ISSUER
        assert principal.verified_subject == "guest-subject-1"
        assert db.scalars(select(TenantIdentityProviderRow)).all() == []
        assert db.scalars(select(TenantMembershipRow)).all() == []
        assert db.scalars(select(UserIdentityRow)).all() == []


def test_real_provider_journey_observes_host_grant_revoke_on_next_request(guest_env) -> None:
    factory, private_key, _, _, raw_state, client = guest_env
    with client:
        response = _redeem(client, raw_state, _token(private_key))
        assert response.status_code == 200
        cookie = _guest_cookie(response)
        assert client.get("/docs/doc-granted", cookies=cookie).status_code == 200
        with factory() as db:
            repo = GuestAdmissionRepository(db, tenant_id="tenant-a")
            assert repo.revoke_document_grant(
                guest_principal_id="guest-1",
                doc_id="doc-granted",
                revoked_at=(NOW + timedelta(minutes=1)).isoformat(),
            )
            db.commit()
        assert client.get("/docs/doc-granted", cookies=cookie).status_code == 404


def test_real_provider_journey_observes_host_principal_revoke_on_next_request(guest_env) -> None:
    factory, private_key, _, _, raw_state, client = guest_env
    with client:
        response = _redeem(client, raw_state, _token(private_key))
        assert response.status_code == 200
        cookie = _guest_cookie(response)
        with factory() as db:
            repo = GuestAdmissionRepository(db, tenant_id="tenant-a")
            assert repo.revoke_guest_principal(
                guest_principal_id="guest-1",
                revoked_at=(NOW + timedelta(minutes=1)).isoformat(),
            )
            db.commit()
        assert client.get("/docs/doc-granted", cookies=cookie).status_code == 401


def test_home_org_and_personal_account_methods_use_same_tenant_independent_crypto_boundary(
    guest_env,
) -> None:
    _, private_key, _, verifier, _, _ = guest_env
    token = _token(private_key)
    personal = verifier.verify_identity(
        credential=token,
        verification_method="personal_account",
    )
    home_org = verifier.verify_identity(
        credential=token,
        verification_method="home_org_idp",
    )
    assert personal == home_org
    assert personal.issuer == ISSUER


def test_unknown_verification_method_fails_closed(guest_env) -> None:
    _, private_key, _, verifier, _, _ = guest_env
    with pytest.raises(GuestIdentityVerificationError):
        verifier.verify_identity(
            credential=_token(private_key),
            verification_method="receiving_tenant_membership",
        )


def test_unknown_provider_and_wrong_audience_fail_closed(guest_env) -> None:
    _, private_key, _, verifier, _, _ = guest_env
    with pytest.raises(GuestIdentityVerificationError):
        verifier.verify_identity(
            credential=_token(private_key, issuer="https://unknown.example.test"),
            verification_method="personal_account",
        )
    with pytest.raises(GuestIdentityVerificationError):
        verifier.verify_identity(
            credential=_token(private_key, audience="wrong-audience"),
            verification_method="personal_account",
        )


def test_invalid_signature_fails_closed(guest_env) -> None:
    _, _, _, verifier, _, _ = guest_env
    attacker_key, _ = _key_pair()
    with pytest.raises(GuestIdentityVerificationError):
        verifier.verify_identity(
            credential=_token(attacker_key),
            verification_method="personal_account",
        )


def test_inactive_provider_fails_closed(guest_env) -> None:
    factory, private_key, _, verifier, _, _ = guest_env
    with factory() as db:
        provider = db.get(IdentityProviderRow, "guest-idp")
        assert provider is not None
        provider.lifecycle_state = "disabled"
        db.commit()
    with pytest.raises(GuestIdentityVerificationError):
        verifier.verify_identity(
            credential=_token(private_key),
            verification_method="personal_account",
        )


def test_jwks_outage_is_distinct_from_bad_identity(guest_env) -> None:
    factory, private_key, _, _, _, _ = guest_env
    verifier = DatabaseJwtGuestIdentityVerifier(
        session_factory=factory,
        jwks_store=JwksStore(),
    )
    with patch("kj_atlas_api.trusted_auth_edge._fetch_jwks", side_effect=OSError):
        with pytest.raises(GuestIdentityVerificationUnavailableError):
            verifier.verify_identity(
                credential=_token(private_key),
                verification_method="personal_account",
            )
