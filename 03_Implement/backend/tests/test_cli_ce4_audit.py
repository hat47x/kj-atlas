from __future__ import annotations

import json
from pathlib import Path

import pytest

from kj_atlas_api import cli


class _DummyResponse:
    def __init__(self, text: str = '{"status":"accepted"}') -> None:
        self.text = text

    def raise_for_status(self) -> None:
        return None


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
    assert request_log["headers"] == {"x-actor-ref": "user:alice", "x-trace-id": "trace-1"}
    assert request_log["timeout"] == 5.0
    assert request_log["json"]["operation"] == "proposal"
    assert request_log["json"]["command"] == "proposal-diff"


def test_main_ce4_resolve_bundle_hits_resolve_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    request_log: dict[str, object] = {}

    def _fake_post(url: str, json: dict[str, object], timeout: float):
        request_log.update({"url": url, "json": json, "timeout": timeout})
        return _DummyResponse('{"bundleHash":"abc"}')

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
    assert request_log["timeout"] == 5.0
