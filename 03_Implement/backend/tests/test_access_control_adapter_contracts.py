from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from kj_atlas_api.access_control import (
    AccessRequest,
    AccessResource,
    AccessSubject,
    build_access_control_adapter,
)


def _sample_request() -> AccessRequest:
    return AccessRequest(
        action="read",
        safe_mode=True,
        read_only=False,
        subject=AccessSubject(actor_ref="user-1", roles=("analyst",), groups=("ops",)),
        resource=AccessResource(doc_id="doc-1", visibility="Restricted", policy_ref="policy-1"),
    )


def test_noop_adapter_allows_by_default() -> None:
    adapter = build_access_control_adapter(adapter_name="noop")
    decision = adapter.authorize(_sample_request())
    assert decision.allow is True


def test_mock_adapter_follows_configured_decision() -> None:
    adapter = build_access_control_adapter(
        adapter_name="mock",
        mock_allow=False,
        mock_reason="mock_denied",
    )

    decision = adapter.authorize(_sample_request())
    assert decision.allow is False
    assert decision.reason == "mock_denied"


def test_http_adapter_posts_passthrough_payload_and_returns_decision() -> None:
    received: dict[str, object] = {}

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):  # noqa: N802
            content_length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(content_length)
            received["path"] = self.path
            received["auth"] = self.headers.get("Authorization")
            received["payload"] = json.loads(body.decode("utf-8"))
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"allow": true, "readOnly": true, "reason": "delegated"}')

        def log_message(self, format, *args):  # noqa: A003, ANN001
            return

    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        adapter = build_access_control_adapter(
            adapter_name="http",
            http_endpoint=f"http://127.0.0.1:{server.server_port}/authorize",
            http_api_key="top-secret",
            http_timeout_seconds=1.0,
        )

        decision = adapter.authorize(_sample_request())
    finally:
        server.shutdown()
        thread.join(timeout=2)

    assert decision.allow is True
    assert decision.read_only is True
    assert decision.reason == "delegated"
    assert received["path"] == "/authorize"
    assert received["auth"] == "Bearer top-secret"
    assert received["payload"] == {
        "action": "read",
        "safeMode": True,
        "readOnly": False,
        "subject": {
            "actorRef": "user-1",
            "roles": ["analyst"],
            "groups": ["ops"],
        },
        "resource": {
            "docId": "doc-1",
            "visibility": "Restricted",
            "policyRef": "policy-1",
        },
    }
