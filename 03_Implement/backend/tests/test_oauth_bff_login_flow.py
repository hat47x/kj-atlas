"""SAAS-TENANT-SESSION-BINDING-01 / ADR-0074 decision 1: the BFF login flow
(GET /session/login, GET /session/callback) shipped without tests.

The security-bearing logic here is small but sharp: an open-redirect guard on
the post-login destination, PKCE challenge derivation, and the ordered set of
guards the callback applies before it will exchange a code. Each is pinned
below.
"""

from __future__ import annotations

import base64
import hashlib
import json
from http.cookies import SimpleCookie
from types import SimpleNamespace
from urllib.parse import parse_qs, urlsplit

import pytest
from fastapi import HTTPException, Request

from kj_atlas_api import oauth_bff
from kj_atlas_api.oauth_bff import (
    _generate_pkce_pair,
    _parse_pending_cookie,
    _validate_next_path,
    handle_callback,
    initiate_login,
)
from kj_atlas_api.settings import settings

PENDING_COOKIE = "Kj-Atlas-Oauth-Pending"


def _request(cookies: dict[str, str] | None = None, runtime_profile: str = "saas-multitenant"):
    app = SimpleNamespace(
        state=SimpleNamespace(
            runtime_profile=runtime_profile,
            saas_oauth_broker_config=None,
        )
    )
    headers: list[tuple[bytes, bytes]] = []
    if cookies:
        joined = "; ".join(f"{name}={value}" for name, value in cookies.items())
        headers.append((b"cookie", joined.encode()))
    return Request(
        scope={
            "type": "http",
            "method": "GET",
            "path": "/session/callback",
            "headers": headers,
            "app": app,
        }
    )


def _pending_cookie_value(state: str = "state-1", verifier: str = "verifier-1", next_path: str = "/") -> str:
    return json.dumps({"state": state, "code_verifier": verifier, "next": next_path})


def _stored_pending(redirect):
    """Read the pending-login cookie back out of Set-Cookie.

    The value is JSON, so Starlette RFC-quotes it (escaped quotes, \\054 for
    commas). SimpleCookie unquotes it the way a browser would; splitting the
    header by hand does not.
    """
    jar: SimpleCookie = SimpleCookie()
    for value in redirect.headers.getlist("set-cookie"):
        jar.load(value)
    morsel = jar.get(PENDING_COOKIE)
    return _parse_pending_cookie(morsel.value if morsel is not None else None)


# --- open-redirect guard ----------------------------------------------------
# Mutation-testing note: _validate_next_path guards in two layers, and the
# second (`parsed.scheme or parsed.netloc`) is currently unreachable -- any
# value that survives the leading-slash checks starts with exactly one "/", and
# such a string can carry neither a scheme nor a netloc. Disabling that line
# fails nothing below. It is left in place as a margin against future edits to
# the earlier checks, but it is not covered here because no input can reach it.


@pytest.mark.parametrize(
    "hostile",
    [
        "//evil.example",  # protocol-relative
        "https://evil.example/pwn",  # absolute
        "http://evil.example",
        "javascript:alert(1)",
        "evil.example/path",  # no leading slash
        "/\r\nSet-Cookie: x=1",  # header injection
        "/\nLocation: https://evil.example",
        "",
    ],
)
def test_next_path_rejects_anything_that_could_leave_this_origin(hostile: str) -> None:
    assert _validate_next_path(hostile) == "/"


def test_next_path_rejects_none_and_overlong_values() -> None:
    assert _validate_next_path(None) == "/"
    assert _validate_next_path("/" + "a" * 4096) == "/"


@pytest.mark.parametrize(
    "allowed",
    ["/", "/docs", "/docs/doc-1", "/docs?tab=cards", "/docs/doc-1#island-2"],
)
def test_next_path_preserves_same_origin_destinations(allowed: str) -> None:
    assert _validate_next_path(allowed) == allowed


# --- PKCE -------------------------------------------------------------------


def test_pkce_challenge_is_the_unpadded_s256_of_the_verifier() -> None:
    """A wrong derivation here would not fail locally -- the broker would just
    reject every exchange -- so pin it against the RFC 7636 construction."""
    verifier, challenge = _generate_pkce_pair()

    expected = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("ascii")).digest())
        .rstrip(b"=")
        .decode("ascii")
    )
    assert challenge == expected
    assert "=" not in challenge


def test_pkce_pairs_are_not_reused_between_logins() -> None:
    first, _ = _generate_pkce_pair()
    second, _ = _generate_pkce_pair()

    assert first != second


# --- pending-login cookie parsing ------------------------------------------


@pytest.mark.parametrize(
    "raw",
    [
        None,
        "",
        "not-json",
        "[]",  # not a dict
        json.dumps({"state": "s"}),  # missing verifier/next
        json.dumps({"state": "", "code_verifier": "v", "next": "/"}),  # blank state
        json.dumps({"state": "s", "code_verifier": "", "next": "/"}),
        json.dumps({"state": "s", "code_verifier": "v", "next": ""}),
        json.dumps({"state": 1, "code_verifier": "v", "next": "/"}),  # wrong type
    ],
)
def test_unusable_pending_cookies_parse_to_none(raw: str | None) -> None:
    assert _parse_pending_cookie(raw) is None


def test_wellformed_pending_cookie_round_trips() -> None:
    parsed = _parse_pending_cookie(_pending_cookie_value(next_path="/docs/doc-1"))

    assert parsed is not None
    assert parsed.state == "state-1"
    assert parsed.code_verifier == "verifier-1"
    assert parsed.next_path == "/docs/doc-1"


# --- GET /session/login -----------------------------------------------------


def _configure_broker(monkeypatch) -> None:
    monkeypatch.setattr(
        settings, "saas_oauth_broker_http_authorize_endpoint", "https://broker.invalid/authorize"
    )
    monkeypatch.setattr(settings, "saas_oauth_broker_http_client_id", "kj-atlas-bff")
    monkeypatch.setattr(
        settings, "saas_oauth_broker_http_redirect_uri", "https://app.invalid/session/callback"
    )


def test_login_is_unavailable_until_the_broker_is_configured(monkeypatch) -> None:
    monkeypatch.setattr(settings, "saas_oauth_broker_http_authorize_endpoint", None)
    monkeypatch.setattr(settings, "saas_oauth_broker_http_client_id", "kj-atlas-bff")
    monkeypatch.setattr(settings, "saas_oauth_broker_http_redirect_uri", "https://app/callback")

    with pytest.raises(HTTPException) as exc:
        initiate_login(request=_request(), next_query=None)

    assert exc.value.status_code == 503
    assert exc.value.detail["code"] == "oauth_login_unavailable"


def test_login_redirects_with_pkce_s256_and_binds_state_to_the_pending_cookie(monkeypatch) -> None:
    _configure_broker(monkeypatch)

    redirect = initiate_login(request=_request(), next_query="/docs/doc-1")

    assert redirect.status_code == 302
    query = parse_qs(urlsplit(redirect.headers["location"]).query)
    assert query["response_type"] == ["code"]
    assert query["code_challenge_method"] == ["S256"]
    assert query["scope"] == ["openid"]

    raw_header = next(
        value
        for value in redirect.headers.getlist("set-cookie")
        if value.startswith(f"{PENDING_COOKIE}=")
    )
    assert "HttpOnly" in raw_header
    # The state in the redirect must be the one stored for later comparison,
    # otherwise the callback's state check could never succeed.
    stored = _stored_pending(redirect)
    assert stored is not None
    assert query["state"] == [stored.state]
    assert stored.next_path == "/docs/doc-1"


def test_login_discards_a_hostile_next_destination(monkeypatch) -> None:
    _configure_broker(monkeypatch)

    redirect = initiate_login(request=_request(), next_query="https://evil.example/pwn")

    stored = _stored_pending(redirect)
    assert stored is not None
    assert stored.next_path == "/"


# --- GET /session/callback guards -------------------------------------------
# Each of these raises before any code exchange or DB access, so db is unused.


def test_callback_without_a_pending_login_is_rejected() -> None:
    with pytest.raises(HTTPException) as exc:
        handle_callback(request=_request(), db=None, code="c", state="s", error=None)

    assert exc.value.status_code == 400
    assert exc.value.detail["code"] == "oauth_login_not_pending"


def test_callback_reports_a_broker_denial() -> None:
    request = _request({PENDING_COOKIE: _pending_cookie_value()})

    with pytest.raises(HTTPException) as exc:
        handle_callback(request=request, db=None, code=None, state="state-1", error="access_denied")

    assert exc.value.status_code == 400
    assert exc.value.detail["code"] == "oauth_broker_denied"


@pytest.mark.parametrize("presented", [None, "", "not-the-stored-state"])
def test_callback_rejects_a_state_that_does_not_match_the_pending_cookie(presented) -> None:
    request = _request({PENDING_COOKIE: _pending_cookie_value(state="stored-state")})

    with pytest.raises(HTTPException) as exc:
        handle_callback(request=request, db=None, code="c", state=presented, error=None)

    assert exc.value.status_code == 400
    assert exc.value.detail["code"] == "oauth_state_mismatch"


def test_callback_requires_an_authorization_code() -> None:
    request = _request({PENDING_COOKIE: _pending_cookie_value()})

    with pytest.raises(HTTPException) as exc:
        handle_callback(request=request, db=None, code=None, state="state-1", error=None)

    assert exc.value.status_code == 400
    assert exc.value.detail["code"] == "oauth_login_not_pending"


def test_callback_fails_closed_when_the_broker_config_is_absent() -> None:
    """State and code are valid here; only the server-side broker config is
    missing, which must not be reported as a client error."""
    request = _request({PENDING_COOKIE: _pending_cookie_value()})
    assert getattr(request.app.state, "saas_oauth_broker_config") is None

    with pytest.raises(HTTPException) as exc:
        handle_callback(request=request, db=None, code="code-1", state="state-1", error=None)

    assert exc.value.status_code == 503
    assert exc.value.detail["code"] == "oauth_broker_unavailable"


def test_state_comparison_uses_a_constant_time_primitive() -> None:
    """The state check must not short-circuit on the first differing byte."""
    source = oauth_bff.__loader__.get_source(oauth_bff.__name__)

    assert "hmac.compare_digest(state, pending.state)" in source
