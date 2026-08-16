from __future__ import annotations

import json
from typing import Any

import pytest

from kj_atlas_api import cli


class _Response:
    def __init__(self, payload: object, *, status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code
        self.is_error = status_code >= 400

    def json(self) -> object:
        return self._payload


def test_control_plane_headers_use_admin_secret_only(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KJ_ATLAS_ADMIN_API_KEY", " admin-secret ")
    monkeypatch.setenv("KJ_ATLAS_API_KEY", "business-secret")

    assert cli._control_plane_headers(actor_ref="operator", trace_id="request-1") == {
        "x-admin-api-key": "admin-secret",
        "x-actor-ref": "operator",
        "x-request-id": "request-1",
    }


def test_admin_models_list_uses_control_plane_and_json_output(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    request_log: dict[str, Any] = {}
    monkeypatch.setenv("KJ_ATLAS_ADMIN_API_KEY", "admin-secret")

    def _request(method: str, url: str, **kwargs: object) -> _Response:
        request_log.update({"method": method, "url": url, **kwargs})
        return _Response({"providers": [], "models": []})

    monkeypatch.setattr(cli.httpx, "request", _request)

    assert cli.main(["--api-base-url", "http://localhost:9999/", "admin", "models", "list"]) == 0
    assert request_log["method"] == "GET"
    assert request_log["url"] == "http://localhost:9999/admin/provision/models"
    assert request_log["headers"] == {"x-admin-api-key": "admin-secret"}
    assert json.loads(capsys.readouterr().out) == {"providers": [], "models": []}


def test_admin_write_requires_explicit_yes_in_automation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called = False

    def _request(*args: object, **kwargs: object) -> _Response:
        nonlocal called
        called = True
        return _Response({"status": "created"}, status_code=201)

    monkeypatch.setattr(cli.httpx, "request", _request)

    with pytest.raises(SystemExit, match="requires --yes"):
        cli.main(
            [
                "admin",
                "providers",
                "register",
                "--id",
                "local",
                "--kind",
                "local",
                "--display-name",
                "Local",
            ]
        )
    assert called is False


def test_allowlist_set_reads_current_state_and_prints_diff(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    calls: list[tuple[str, str, dict[str, object] | None]] = []

    def _request(method: str, url: str, **kwargs: object) -> _Response:
        payload = kwargs.get("json")
        calls.append((method, url, payload if isinstance(payload, dict) else None))
        if method == "GET":
            return _Response({"tenantId": "tenant a", "modelIds": ["old-model"]})
        return _Response({"tenantId": "tenant a", "modelIds": ["new-model"]})

    monkeypatch.setattr(cli.httpx, "request", _request)

    assert (
        cli.main(
            [
                "admin",
                "tenants",
                "model-allowlist-set",
                "--tenant-id",
                "tenant a",
                "--model-id",
                "new-model",
                "--yes",
            ]
        )
        == 0
    )

    assert calls == [
        (
            "GET",
            "http://127.0.0.1:8000/admin/provision/models/tenants/tenant%20a/allowlist",
            None,
        ),
        (
            "PUT",
            "http://127.0.0.1:8000/admin/provision/models/tenants/tenant%20a/allowlist",
            {"modelIds": ["new-model"]},
        ),
    ]
    captured = capsys.readouterr()
    preview = json.loads(captured.err)["changePreview"]
    assert preview["added"] == ["new-model"]
    assert preview["removed"] == ["old-model"]


def test_admin_error_is_structured_and_never_echoes_secret(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    secret = "do-not-print-this-admin-secret"
    monkeypatch.setenv("KJ_ATLAS_ADMIN_API_KEY", secret)
    monkeypatch.setattr(
        cli.httpx,
        "request",
        lambda *args, **kwargs: _Response(
            {
                "detail": {
                    "code": "control_plane_unauthorized",
                    "message": "Control plane authorization is required.",
                }
            },
            status_code=401,
        ),
    )

    with pytest.raises(SystemExit) as raised:
        cli.main(["admin", "audit", "list"])

    assert raised.value.code == 2
    error_output = capsys.readouterr().err
    assert json.loads(error_output)["error"]["code"] == "control_plane_unauthorized"
    assert secret not in error_output


def test_admin_secret_cannot_be_supplied_as_cli_option() -> None:
    with pytest.raises(SystemExit) as raised:
        cli._parse_args(["--admin-api-key", "secret", "admin", "models", "list"])
    assert raised.value.code == 2
