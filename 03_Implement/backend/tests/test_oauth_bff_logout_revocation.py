"""SAAS-TENANT-SESSION-BINDING-01 / ADR-0074 decision 6: logout must revoke the
auth session it was presented with.

Before this, POST /session/logout cleared only the tenant-version cookie:
the BFF auth-session row stayed live and its cookie stayed in the browser, so
"logging out" left a usable credential behind. revoke_auth_session_cookie also
gave DatabaseSaasAuthSessionStore.revoke_auth_session its first caller.
"""

from __future__ import annotations

from types import SimpleNamespace

from fastapi import Request, Response
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from kj_atlas_api.auth_session_hash import derive_session_key_hash
from kj_atlas_api.models import Base
from kj_atlas_api.oauth_bff import revoke_auth_session_cookie
from kj_atlas_api.saas_auth_state import DatabaseSaasAuthSessionStore

COOKIE_NAME = "Kj-Atlas-Auth-Session"
HASH_KEY = b"logout-revocation-test-key-01234"
ISSUER = "https://broker.invalid/issuer"
RAW_SESSION = "opaque-logout-session-value"


def _store(tmp_path) -> DatabaseSaasAuthSessionStore:
    engine = create_engine(
        f"sqlite:///{tmp_path}/logout.db",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)
    return DatabaseSaasAuthSessionStore(factory)


def _login(store: DatabaseSaasAuthSessionStore, raw: str = RAW_SESSION) -> str:
    key_hash = derive_session_key_hash(raw, key=HASH_KEY)
    store.create_auth_session(
        session_key_hash=key_hash,
        principal_id="user-1",
        issuer=ISSUER,
        subject="subject-1",
        active_tenant_id=None,
        tenant_session_version="version-1",
    )
    return key_hash


def _request(
    cookie: str | None = RAW_SESSION,
    store: DatabaseSaasAuthSessionStore | None = None,
    hash_key: bytes | None = HASH_KEY,
    runtime_profile: str = "saas-multitenant",
) -> Request:
    app = SimpleNamespace(
        state=SimpleNamespace(
            saas_auth_session_store=store,
            saas_auth_session_hash_key=hash_key,
            runtime_profile=runtime_profile,
        )
    )
    headers: list[tuple[bytes, bytes]] = []
    if cookie is not None:
        headers.append((b"cookie", f"{COOKIE_NAME}={cookie}".encode()))
    return Request(
        scope={
            "type": "http",
            "method": "POST",
            "path": "/session/logout",
            "headers": headers,
            "app": app,
        }
    )


def _cleared_cookie_headers(response: Response) -> list[str]:
    return [
        value
        for value in response.headers.getlist("set-cookie")
        if value.startswith(f"{COOKIE_NAME}=")
    ]


def test_logout_revokes_the_presented_session(tmp_path) -> None:
    store = _store(tmp_path)
    key_hash = _login(store)
    assert store.resolve_auth_session(session_key_hash=key_hash) is not None

    revoke_auth_session_cookie(request=_request(store=store), response=Response())

    assert store.resolve_auth_session(session_key_hash=key_hash) is None


def test_logout_clears_the_auth_session_cookie(tmp_path) -> None:
    store = _store(tmp_path)
    _login(store)
    response = Response()

    revoke_auth_session_cookie(request=_request(store=store), response=response)

    cleared = _cleared_cookie_headers(response)
    assert cleared, "logout must emit a Set-Cookie clearing the auth-session cookie"
    assert "Max-Age=0" in cleared[0]
    assert "HttpOnly" in cleared[0]


def test_logout_does_not_revoke_a_different_login_of_the_same_principal(tmp_path) -> None:
    """ADR-0074 decision 6: logout ends the presented session only. Signing out
    of one browser must not sign the same user out everywhere."""
    store = _store(tmp_path)
    presented = _login(store)
    other = _login(store, raw="a-second-browser-session")

    revoke_auth_session_cookie(request=_request(store=store), response=Response())

    assert store.resolve_auth_session(session_key_hash=presented) is None
    assert store.resolve_auth_session(session_key_hash=other) is not None


def test_logout_without_an_auth_session_cookie_still_clears(tmp_path) -> None:
    store = _store(tmp_path)
    response = Response()

    revoke_auth_session_cookie(request=_request(cookie=None, store=store), response=response)

    assert _cleared_cookie_headers(response)


def test_logout_clears_the_cookie_even_when_no_store_is_configured() -> None:
    """single-tenant profiles never wire the auth-session store; logout must
    still clear the cookie rather than raise."""
    response = Response()

    revoke_auth_session_cookie(
        request=_request(store=None, hash_key=None, runtime_profile="local-dev"),
        response=response,
    )

    assert _cleared_cookie_headers(response)
