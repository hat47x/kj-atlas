from __future__ import annotations

from urllib import request as urllib_request

from kj_atlas_api.trusted_http import _RejectRedirectHandler, open_trusted_http


def test_trusted_http_redirect_handler_does_not_create_forward_request() -> None:
    outbound = urllib_request.Request(
        "https://trusted.example/start",
        data=b"{}",
        headers={"Authorization": "Bearer redirect-secret"},
        method="POST",
    )

    redirected = _RejectRedirectHandler().redirect_request(
        outbound,
        None,
        302,
        "Found",
        {},
        "https://untrusted.example/sink",
    )

    assert redirected is None


def test_trusted_http_installs_redirect_rejection_handler(monkeypatch) -> None:  # noqa: ANN001
    captured: dict[str, object] = {}
    response = object()

    class _Opener:
        def open(self, request, timeout):  # noqa: ANN001
            captured["request"] = request
            captured["timeout"] = timeout
            return response

    def _build_opener(*handlers):  # noqa: ANN001
        captured["handlers"] = handlers
        return _Opener()

    monkeypatch.setattr(urllib_request, "build_opener", _build_opener)
    outbound = urllib_request.Request("https://trusted.example/start")

    result = open_trusted_http(outbound, timeout_seconds=1.25)

    assert result is response
    assert captured["request"] is outbound
    assert captured["timeout"] == 1.25
    assert any(
        isinstance(handler, _RejectRedirectHandler)
        for handler in captured["handlers"]
    )
