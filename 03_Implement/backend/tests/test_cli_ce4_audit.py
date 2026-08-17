from __future__ import annotations

import json
from pathlib import Path

import pytest

from kj_atlas_api import cli
from kj_atlas_api.audit import CE4_AUDIT_REQUIRED_FIELDS, CE4_AUDIT_SCHEMA_VERSION


class _DummyResponse:
    def __init__(self, payload: dict[str, object] | None = None) -> None:
        self._payload = payload or {"status": "accepted"}
        self.text = json.dumps(self._payload)

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, object]:
        return self._payload


def _write_payload(tmp_path: Path, payload: dict[str, object]) -> Path:
    file_path = tmp_path / "payload.json"
    file_path.write_text(json.dumps(payload), encoding="utf-8")
    return file_path


def test_build_payload_for_apply_forces_dry_run_and_none_side_effect() -> None:
    args = cli._parse_args(["apply", "--input", "dummy.json", "--no-safe-mode"])
    doc_id, payload = cli._build_payload(
        args,
        {
            "docId": "doc-1",
            "equivalenceKey": "a" * 64,
            "bundleHash": "b" * 64,
            "sourceBundleHash": "c" * 64,
            "sideEffect": "should-be-overridden",
        },
    )

    assert doc_id == "doc-1"
    assert payload["operation"] == "apply"
    assert payload["dryRun"] is True
    assert payload["sideEffect"] == "none"
    assert payload["command"] == "apply --dry-run"
    assert payload["channel"] == "cli"
    assert payload["safeMode"] is False


@pytest.mark.parametrize("missing_key", ["equivalenceKey", "bundleHash"])
def test_build_payload_requires_ce4_hash_keys(missing_key: str) -> None:
    args = cli._parse_args(["context-query", "--input", "dummy.json"])
    payload = {"docId": "doc-1", "equivalenceKey": "a" * 64, "bundleHash": "b" * 64}
    payload.pop(missing_key)

    with pytest.raises(SystemExit):
        cli._build_payload(args, payload)


def test_main_posts_context_audit_payload_and_headers(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    request_log: dict[str, object] = {}
    monkeypatch.setenv("KJ_ATLAS_API_KEY", "business-secret")

    def _fake_post(url: str, json: dict[str, object], headers: dict[str, str], timeout: float):
        request_log.update({"url": url, "json": json, "headers": headers, "timeout": timeout})
        return _DummyResponse()

    monkeypatch.setattr(cli.httpx, "post", _fake_post)

    payload_file = _write_payload(
        tmp_path,
        {
            "docId": "doc-42",
            "equivalenceKey": "a" * 64,
            "bundleHash": "b" * 64,
            "sourceBundleHash": "c" * 64,
            "queryHash": "a" * 64,
        },
    )

    exit_code = cli.main(
        [
            "--api-base-url",
            "http://localhost:9999",
            "--actor-ref",
            "user:alice",
            "--trace-id",
            "trace-1",
            "proposal-diff",
            "--input",
            str(payload_file),
        ]
    )

    assert exit_code == 0
    assert request_log["url"] == "http://localhost:9999/docs/doc-42/context-audit"
    assert request_log["headers"] == {
        "x-api-key": "business-secret",
        "x-actor-ref": "user:alice",
        "x-trace-id": "trace-1",
    }
    assert request_log["timeout"] == 5.0
    assert request_log["json"]["operation"] == "proposal"
    assert request_log["json"]["command"] == "proposal-diff"


def test_main_ce4_resolve_bundle_hits_resolve_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    request_log: dict[str, object] = {}
    monkeypatch.setenv("KJ_ATLAS_API_KEY", "business-secret")

    def _fake_post(url: str, json: dict[str, object], headers: dict[str, str], timeout: float):
        request_log.update({"url": url, "json": json, "headers": headers, "timeout": timeout})
        return _DummyResponse(
            {
                "equivalenceKey": "a" * 64,
                "bundleHash": "b" * 64,
                "queryCanonicalHash": "c" * 64,
                "proposalLifecycle": "proposed",
                "sideEffect": "none",
                "auditChain": {"query": "1", "bundle": "2", "proposal": "3", "apply": "4"},
            }
        )

    monkeypatch.setattr(cli.httpx, "post", _fake_post)

    exit_code = cli.main(
        [
            "--api-base-url",
            "http://localhost:9999",
            "ce4",
            "resolve-bundle",
            "--query",
            "test query",
            "--source-bundle-hash",
            "d" * 64,
            "--no-safe-mode",
        ]
    )

    assert exit_code == 0
    assert request_log["url"] == "http://localhost:9999/context/bundles:resolve"
    assert request_log["json"] == {
        "query": "test query",
        "dryRun": True,
        "sourceBundleHash": "d" * 64,
        "safeMode": False,
    }
    assert request_log["headers"] == {"x-api-key": "business-secret"}
    assert request_log["timeout"] == 5.0


def test_business_plane_headers_omit_unset_or_blank_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("KJ_ATLAS_API_KEY", raising=False)
    assert cli._business_plane_headers() == {}

    monkeypatch.setenv("KJ_ATLAS_API_KEY", "   ")
    assert cli._business_plane_headers(actor_ref="operator") == {"x-actor-ref": "operator"}


def test_build_payload_prefers_query_canonical_hash_when_present() -> None:
    args = cli._parse_args(["context-query", "--input", "dummy.json"])
    _, payload = cli._build_payload(
        args,
        {
            "docId": "doc-1",
            "equivalenceKey": "a" * 64,
            "bundleHash": "b" * 64,
            "queryHash": "c" * 64,
            "queryCanonicalHash": "d" * 64,
        },
    )

    assert payload["queryHash"] == "d" * 64


def test_build_payload_normalizes_ce4_contract_fields_only() -> None:
    args = cli._parse_args(["context-query", "--input", "dummy.json"])
    _, payload = cli._build_payload(
        args,
        {
            "docId": "doc-1",
            "equivalenceKey": "a" * 64,
            "bundleHash": "b" * 64,
            "ignoredInput": "must-not-pass-through",
        },
    )

    assert set(payload.keys()) == set(CE4_AUDIT_REQUIRED_FIELDS)
    assert payload["schemaVersion"] == CE4_AUDIT_SCHEMA_VERSION
    assert "ignoredInput" not in payload


def test_main_ce4_resolve_bundle_fail_closed_when_response_missing_required_field(monkeypatch: pytest.MonkeyPatch) -> None:
    def _fake_post(url: str, json: dict[str, object], headers: dict[str, str], timeout: float):
        return _DummyResponse({"bundleHash": "abc"})

    monkeypatch.setattr(cli.httpx, "post", _fake_post)

    with pytest.raises(SystemExit, match="missing response field"):
        cli.main(["ce4", "resolve-bundle", "--query", "q", "--source-bundle-hash", "x" * 64])


def test_main_ce4_resolve_bundle_fail_closed_when_dry_run_side_effect_is_not_none(monkeypatch: pytest.MonkeyPatch) -> None:
    def _fake_post(url: str, json: dict[str, object], headers: dict[str, str], timeout: float):
        return _DummyResponse(
            {
                "equivalenceKey": "a" * 64,
                "bundleHash": "b" * 64,
                "queryCanonicalHash": "c" * 64,
                "proposalLifecycle": "proposed",
                "sideEffect": "write",
                "auditChain": {"query": "1", "bundle": "2", "proposal": "3", "apply": "4"},
            }
        )

    monkeypatch.setattr(cli.httpx, "post", _fake_post)

    with pytest.raises(SystemExit, match="dryRun=true requires sideEffect=none"):
        cli.main(["ce4", "resolve-bundle", "--query", "q", "--source-bundle-hash", "x" * 64])
