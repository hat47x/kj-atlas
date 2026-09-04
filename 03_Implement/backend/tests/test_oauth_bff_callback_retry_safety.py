"""AUTH-ONE-TIME-JWT-01 AC-6/AC-7 (post-ADR-0074 B-model reinterpretation):

AC-6 asks whether an ambiguous/timed-out retry of a mutating request fails
closed instead of silently double-applying. The BFF login mutation
(GET /session/callback) is exactly this shape: a browser that never saw the
first response (network timeout, tab closed mid-redirect) resubmits the same
`code`/`state` against the same still-present `Kj-Atlas-Oauth-Pending`
cookie. OAuth 2.0 authorization codes are single-use by construction (both
the mock IdP in tests/level2/mock_idp.py and any real broker delete/consume
the code on first exchange), so the retry's `exchange_code_for_tokens` call
fails with OauthBrokerInvalidResponseError -- handle_callback already maps
that to a 400. This test proves the *consequence* that AC-6 actually cares
about: the retry does not create a second SaasAuthSessionRow. A duplicate
session row is the concrete "mutation executed twice" outcome that matters
here (a duplicate would double-count active sessions and could outlive the
one the user believes they have).

AC-7 asks whether the SPA ever receives a refresh token or other long-lived
credential. handle_callback's redirect response is asserted here to never
contain the broker-issued access token value anywhere in its headers --
closing the loop on top of oauth_broker_client.py's BrokerTokenResponse,
which structurally has no refresh_token field at all (see
test_oauth_broker_client.py::test_exchange_drops_the_refresh_token_even_when_the_broker_returns_one).

Both properties are pinned at the handle_callback level (not a full mock-IdP
network round trip): _verify_broker_identity and exchange_code_for_tokens are
monkeypatched at their call sites in oauth_bff.py, exactly as
test_oauth_bff_login_flow.py already does for its guard-clause tests. This
keeps the real business logic under test (pending-cookie/state validation,
session creation, cookie issuance) while isolating the two external
boundaries (broker HTTP call, JWKS/JWT verification) this test does not need
to exercise.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest
from fastapi import Request
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker

from kj_atlas_api import oauth_bff
from kj_atlas_api.models import Base, SaasAuthSessionRow, TenantRow
from kj_atlas_api.oauth_broker_client import (
    BrokerTokenResponse,
    ExternalOauthBrokerConfig,
    OauthBrokerInvalidResponseError,
)
from kj_atlas_api.saas_auth_state import DatabaseSaasAuthSessionStore
from kj_atlas_api.tenant_context import VerifiedTenantClaim

_FAKE_ACCESS_TOKEN = "atk-should-never-reach-the-browser"
_HASH_KEY = b"callback-retry-safety-test-key-0123"


def _factory(tmp_path):
    engine = create_engine(
        f"sqlite:///{tmp_path / 'callback-retry.db'}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, class_=Session, expire_on_commit=False)


def _seed_tenant(factory, tenant_id: str) -> None:
    now = datetime.now(timezone.utc).isoformat()
    with factory() as db:
        db.add(
            TenantRow(
                id=tenant_id,
                display_name=tenant_id,
                lifecycle_state="active",
                created_at=now,
                updated_at=now,
            )
        )
        db.commit()


def _request(*, store, factory) -> Request:
    from types import SimpleNamespace

    app = SimpleNamespace(
        state=SimpleNamespace(
            runtime_profile="saas-multitenant",
            saas_oauth_broker_config=ExternalOauthBrokerConfig(
                token_endpoint="https://broker.invalid/token",
                client_id="kj-atlas-bff",
                client_secret="broker-secret",
                redirect_uri="https://app.invalid/session/callback",
            ),
            saas_auth_session_store=store,
            saas_auth_session_hash_key=_HASH_KEY,
        )
    )
    pending = json.dumps({"state": "state-1", "code_verifier": "verifier-1", "next": "/docs/doc-1"})
    headers = [(b"cookie", f"Kj-Atlas-Oauth-Pending={pending}".encode())]
    return Request(
        scope={
            "type": "http",
            "method": "GET",
            "path": "/session/callback",
            "headers": headers,
            "app": app,
        }
    )


def _row_count(factory) -> int:
    with factory() as db:
        return db.execute(select(func.count()).select_from(SaasAuthSessionRow)).scalar_one()


def test_retrying_the_same_code_after_success_does_not_create_a_second_session(
    tmp_path,
    monkeypatch,
) -> None:
    factory = _factory(tmp_path)
    _seed_tenant(factory, "tenant-a")
    store = DatabaseSaasAuthSessionStore(factory)

    monkeypatch.setattr(
        oauth_bff,
        "_verify_broker_identity",
        lambda *, db, token: (
            "user-1",
            VerifiedTenantClaim(
                tenant_id="tenant-a",
                identity_provider_id="idp-1",
                issuer="https://idp.example.test",
                audience="kj-atlas",
                subject="subject-1",
            ),
        ),
    )

    call_count = {"n": 0}

    def fake_exchange(*, config, code, code_verifier):
        call_count["n"] += 1
        if call_count["n"] == 1:
            return BrokerTokenResponse(
                access_token=_FAKE_ACCESS_TOKEN,
                token_type="Bearer",
                expires_in=3600,
                id_token=None,
            )
        # OAuth authorization codes are single-use: a real broker (and the
        # mock IdP in tests/level2/mock_idp.py, which deletes the code from
        # _pending_codes on first exchange) rejects a second exchange of the
        # same code with invalid_grant.
        raise OauthBrokerInvalidResponseError("code already used")

    monkeypatch.setattr(oauth_bff, "exchange_code_for_tokens", fake_exchange)

    with factory() as db:
        first = oauth_bff.handle_callback(
            request=_request(store=store, factory=factory),
            db=db,
            code="code-1",
            state="state-1",
            error=None,
        )

    assert first.status_code == 302
    assert first.headers["location"] == "/docs/doc-1"
    assert _row_count(factory) == 1

    # AC-7: the redirect that hands the browser its session must never carry
    # the broker-issued access token anywhere (Set-Cookie values included --
    # the auth-session cookie is a fresh opaque secrets.token_urlsafe(32)
    # value, not the broker token).
    for header_value in first.raw_headers:
        assert _FAKE_ACCESS_TOKEN.encode() not in header_value[1]

    with pytest.raises(Exception) as exc_info:
        with factory() as db:
            oauth_bff.handle_callback(
                request=_request(store=store, factory=factory),
                db=db,
                code="code-1",
                state="state-1",
                error=None,
            )
    from fastapi import HTTPException

    assert isinstance(exc_info.value, HTTPException)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail["code"] == "oauth_broker_rejected"

    # AC-6: the ambiguous retry must fail closed, not mint a second session.
    assert _row_count(factory) == 1
    assert call_count["n"] == 2
