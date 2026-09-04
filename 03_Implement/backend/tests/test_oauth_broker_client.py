from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import error as urllib_error
from urllib.parse import parse_qs

import pytest

from kj_atlas_api.oauth_broker_client import (
    MAX_TOKEN_RESPONSE_BYTES,
    BrokerTokenResponse,
    ExternalOauthBrokerConfig,
    OauthBrokerInvalidResponseError,
    OauthBrokerUnavailableError,
    exchange_code_for_tokens,
)


class _Response:
    def __init__(self, body: bytes) -> None:
        self._body = body

    def read(self, limit: int) -> bytes:
        return self._body[:limit]

    def __enter__(self) -> _Response:
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:  # noqa: ANN001
        return False


def _config(*, token_endpoint: str, timeout_seconds: float = 1.0) -> ExternalOauthBrokerConfig:
    return ExternalOauthBrokerConfig(
        token_endpoint=token_endpoint,
        client_id="client-1",
        client_secret="secret-1",
        redirect_uri="https://app.example.invalid/session/callback",
        timeout_seconds=timeout_seconds,
    )


class _QuietHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):  # noqa: A002, ANN001
        return


def _run_server(handler_cls: type[BaseHTTPRequestHandler]):
    server = HTTPServer(("127.0.0.1", 0), handler_cls)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def test_exchange_sends_form_encoded_request_and_returns_tokens() -> None:
    received: dict[str, object] = {}

    class Handler(_QuietHandler):
        def do_POST(self):  # noqa: N802
            content_length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(content_length)
            received["path"] = self.path
            received["content_type"] = self.headers.get("Content-type")
            received["accept"] = self.headers.get("Accept")
            received["body"] = parse_qs(body.decode("utf-8"))
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps(
                    {
                        "access_token": "atk-1",
                        "token_type": "Bearer",
                        "expires_in": 3600,
                        "id_token": "idt-1",
                    }
                ).encode("utf-8")
            )

    server, thread = _run_server(Handler)
    try:
        config = _config(token_endpoint=f"http://127.0.0.1:{server.server_port}/token")
        result = exchange_code_for_tokens(config=config, code="code-1", code_verifier="verifier-1")
    finally:
        server.shutdown()
        thread.join(timeout=2)

    assert result == BrokerTokenResponse(
        access_token="atk-1", token_type="Bearer", expires_in=3600, id_token="idt-1"
    )
    assert received["path"] == "/token"
    assert received["content_type"] == "application/x-www-form-urlencoded"
    assert received["accept"] == "application/json"
    assert received["body"] == {
        "grant_type": ["authorization_code"],
        "code": ["code-1"],
        "redirect_uri": ["https://app.example.invalid/session/callback"],
        "client_id": ["client-1"],
        "client_secret": ["secret-1"],
        "code_verifier": ["verifier-1"],
    }


def test_exchange_drops_the_refresh_token_even_when_the_broker_returns_one() -> None:
    """AUTH-ONE-TIME-JWT-01 AC-7 / ADR-0074 decision 1: a refresh token must
    never reach the SPA. BrokerTokenResponse (the only value this module
    hands back to its caller, oauth_bff.handle_callback) has no refresh_token
    field at all, so a refresh token the broker includes in its JSON response
    is parsed out of the payload and then has nowhere further to go -- it is
    not stored on the returned object, not logged, and not forwarded. This
    pins that structural guarantee: even a broker response containing
    refresh_token is accepted (refresh_token is in _ALLOWED_TOKEN_RESPONSE_KEYS,
    so the response is not rejected outright), but the token value itself does
    not survive the call."""

    class Handler(_QuietHandler):
        def do_POST(self):  # noqa: N802
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps(
                    {
                        "access_token": "atk-1",
                        "token_type": "Bearer",
                        "expires_in": 3600,
                        "refresh_token": "long-lived-secret-should-not-survive",
                    }
                ).encode("utf-8")
            )

    server, thread = _run_server(Handler)
    try:
        config = _config(token_endpoint=f"http://127.0.0.1:{server.server_port}/token")
        result = exchange_code_for_tokens(config=config, code="code-1", code_verifier="verifier-1")
    finally:
        server.shutdown()
        thread.join(timeout=2)

    assert result == BrokerTokenResponse(
        access_token="atk-1", token_type="Bearer", expires_in=3600, id_token=None
    )
    assert not hasattr(result, "refresh_token")
    assert "long-lived-secret-should-not-survive" not in repr(result)
    assert "refresh_token" not in BrokerTokenResponse.__dataclass_fields__


def test_exchange_does_not_follow_redirect() -> None:
    """Mutation guard: deleting _RejectRedirectHandler in open_trusted_http()
    would make this test follow the redirect instead of failing closed."""
    followed = False

    class RedirectHandler(_QuietHandler):
        def do_POST(self):  # noqa: N802
            nonlocal followed
            if self.path == "/token":
                self.send_response(302)
                self.send_header("Location", f"http://127.0.0.1:{self.server.server_port}/must-not-be-followed")
                self.end_headers()
            else:
                followed = True
                self.send_response(200)
                self.end_headers()

    server, thread = _run_server(RedirectHandler)
    try:
        config = _config(token_endpoint=f"http://127.0.0.1:{server.server_port}/token")
        with pytest.raises(OauthBrokerUnavailableError):
            exchange_code_for_tokens(config=config, code="code-1", code_verifier="verifier-1")
    finally:
        server.shutdown()
        thread.join(timeout=2)

    assert followed is False


@pytest.mark.parametrize("status_code", [400, 401, 403, 404, 409, 422])
def test_exchange_maps_rejected_status_codes_to_invalid_response(status_code: int) -> None:
    class Handler(_QuietHandler):
        def do_POST(self):  # noqa: N802
            self.send_response(status_code)
            self.end_headers()

    server, thread = _run_server(Handler)
    try:
        config = _config(token_endpoint=f"http://127.0.0.1:{server.server_port}/token")
        with pytest.raises(OauthBrokerInvalidResponseError):
            exchange_code_for_tokens(config=config, code="code-1", code_verifier="verifier-1")
    finally:
        server.shutdown()
        thread.join(timeout=2)


def test_exchange_maps_server_error_to_unavailable() -> None:
    class Handler(_QuietHandler):
        def do_POST(self):  # noqa: N802
            self.send_response(500)
            self.end_headers()

    server, thread = _run_server(Handler)
    try:
        config = _config(token_endpoint=f"http://127.0.0.1:{server.server_port}/token")
        with pytest.raises(OauthBrokerUnavailableError):
            exchange_code_for_tokens(config=config, code="code-1", code_verifier="verifier-1")
    finally:
        server.shutdown()
        thread.join(timeout=2)


def test_exchange_maps_timeout_to_unavailable() -> None:
    import time

    class Handler(_QuietHandler):
        def do_POST(self):  # noqa: N802
            time.sleep(0.5)
            self.send_response(200)
            self.end_headers()

    server, thread = _run_server(Handler)
    try:
        config = _config(token_endpoint=f"http://127.0.0.1:{server.server_port}/token", timeout_seconds=0.05)
        with pytest.raises(OauthBrokerUnavailableError):
            exchange_code_for_tokens(config=config, code="code-1", code_verifier="verifier-1")
    finally:
        server.shutdown()
        thread.join(timeout=2)


def test_exchange_rejects_response_exceeding_byte_cap(monkeypatch: pytest.MonkeyPatch) -> None:
    oversized = json.dumps({"access_token": "x" * MAX_TOKEN_RESPONSE_BYTES}).encode("utf-8")
    monkeypatch.setattr(
        "kj_atlas_api.oauth_broker_client.open_trusted_http",
        lambda request, timeout_seconds: _Response(oversized),  # noqa: ARG005
    )

    with pytest.raises(OauthBrokerInvalidResponseError):
        exchange_code_for_tokens(
            config=_config(token_endpoint="http://127.0.0.1:1/token"),
            code="code-1",
            code_verifier="verifier-1",
        )


@pytest.mark.parametrize(
    "body",
    [
        b"not-json",
        json.dumps({}).encode(),
        json.dumps({"access_token": "atk", "token_type": "Bearer", "expires_in": 3600, "extra": "x"}).encode(),
        json.dumps({"access_token": "", "token_type": "Bearer", "expires_in": 3600}).encode(),
        json.dumps({"access_token": "atk", "token_type": "", "expires_in": 3600}).encode(),
        json.dumps({"access_token": "atk", "token_type": "Bearer", "expires_in": 0}).encode(),
        json.dumps({"access_token": "atk", "token_type": "Bearer", "expires_in": True}).encode(),
    ],
    ids=[
        "not-json",
        "empty-object",
        "unexpected-field",
        "empty-access-token",
        "empty-token-type",
        "zero-expires-in",
        "bool-expires-in",
    ],
)
def test_exchange_rejects_malformed_response(monkeypatch: pytest.MonkeyPatch, body: bytes) -> None:
    monkeypatch.setattr(
        "kj_atlas_api.oauth_broker_client.open_trusted_http",
        lambda request, timeout_seconds: _Response(body),  # noqa: ARG005
    )

    with pytest.raises(OauthBrokerInvalidResponseError):
        exchange_code_for_tokens(
            config=_config(token_endpoint="http://127.0.0.1:1/token"),
            code="code-1",
            code_verifier="verifier-1",
        )


def test_exchange_treats_non_string_id_token_as_absent(monkeypatch: pytest.MonkeyPatch) -> None:
    """The mock IdP's id_token is a claims dict, not a JWT string (legacy SP
    compatibility) -- the caller must fall back to access_token, never crash."""
    body = json.dumps(
        {
            "access_token": "atk-1",
            "token_type": "Bearer",
            "expires_in": 3600,
            "id_token": {"sub": "user-1"},
        }
    ).encode("utf-8")
    monkeypatch.setattr(
        "kj_atlas_api.oauth_broker_client.open_trusted_http",
        lambda request, timeout_seconds: _Response(body),  # noqa: ARG005
    )

    result = exchange_code_for_tokens(
        config=_config(token_endpoint="http://127.0.0.1:1/token"),
        code="code-1",
        code_verifier="verifier-1",
    )

    assert result.id_token is None
    assert result.access_token == "atk-1"


def test_exchange_normalizes_url_error_to_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    def _raise(request, timeout_seconds):  # noqa: ANN001, ARG001
        raise urllib_error.URLError("internal service location")

    monkeypatch.setattr("kj_atlas_api.oauth_broker_client.open_trusted_http", _raise)

    with pytest.raises(OauthBrokerUnavailableError):
        exchange_code_for_tokens(
            config=_config(token_endpoint="http://127.0.0.1:1/token"),
            code="code-1",
            code_verifier="verifier-1",
        )
