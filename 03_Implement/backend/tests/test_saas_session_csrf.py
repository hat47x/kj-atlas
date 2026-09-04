from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from kj_atlas_api.session_csrf import (
    AUTH_SESSION_COOKIE,
    CSRF_COOKIE,
    CSRF_HEADER,
    BffCsrfProtectionMiddleware,
    derive_session_csrf_token,
)

KEY = bytes.fromhex("11" * 32)


def _app(*, key: bytes | None = KEY) -> FastAPI:
    app = FastAPI()
    app.state.saas_auth_session_hash_key = key
    app.add_middleware(BffCsrfProtectionMiddleware)

    @app.get("/resource")
    def read_resource():
        return {"ok": True}

    @app.post("/resource", status_code=204)
    def mutate_resource():
        return None

    return app


def _csrf(raw_session_id: str) -> str:
    return derive_session_csrf_token(raw_session_id, key=KEY)


def _cookie_client(raw_session_id: str = "session-a", *, key: bytes | None = KEY) -> TestClient:
    client = TestClient(_app(key=key))
    client.cookies.set(AUTH_SESSION_COOKIE, raw_session_id)
    client.cookies.set(CSRF_COOKIE, _csrf(raw_session_id))
    return client


def test_valid_same_origin_session_bound_header_allows_unsafe_request() -> None:
    client = _cookie_client()
    response = client.post(
        "/resource",
        headers={"Origin": "http://testserver", CSRF_HEADER: _csrf("session-a")},
    )
    assert response.status_code == 204


def test_missing_csrf_header_is_rejected() -> None:
    client = _cookie_client()
    response = client.post("/resource", headers={"Origin": "http://testserver"})
    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "csrf_validation_failed"


def test_token_from_another_session_is_rejected() -> None:
    client = _cookie_client("session-a")
    response = client.post(
        "/resource",
        headers={"Origin": "http://testserver", CSRF_HEADER: _csrf("session-b")},
    )
    assert response.status_code == 403


def test_tampered_token_is_rejected() -> None:
    client = _cookie_client()
    token = _csrf("session-a")
    response = client.post(
        "/resource",
        headers={"Origin": "http://testserver", CSRF_HEADER: token[:-1] + ("0" if token[-1] != "0" else "1")},
    )
    assert response.status_code == 403


def test_cross_site_origin_is_rejected_even_with_correct_token() -> None:
    client = _cookie_client()
    response = client.post(
        "/resource",
        headers={"Origin": "https://evil.example", CSRF_HEADER: _csrf("session-a")},
    )
    assert response.status_code == 403


def test_missing_origin_is_rejected_even_with_correct_token() -> None:
    client = _cookie_client()
    response = client.post("/resource", headers={CSRF_HEADER: _csrf("session-a")})
    assert response.status_code == 403


def test_safe_method_does_not_require_csrf_header() -> None:
    client = _cookie_client()
    assert client.get("/resource").status_code == 200


def test_bearer_priority_path_does_not_require_cookie_csrf() -> None:
    client = _cookie_client()
    response = client.post(
        "/resource",
        headers={"X-Kj-Atlas-Authorization": "Bearer malformed-but-present"},
    )
    assert response.status_code == 204


def test_unsafe_cookie_request_fails_closed_when_server_key_is_unavailable() -> None:
    client = _cookie_client(key=None)
    response = client.post(
        "/resource",
        headers={"Origin": "http://testserver", CSRF_HEADER: _csrf("session-a")},
    )
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "csrf_protection_unavailable"


def test_no_auth_session_cookie_leaves_auth_decision_to_route() -> None:
    client = TestClient(_app())
    response = client.post("/resource")
    assert response.status_code == 204
