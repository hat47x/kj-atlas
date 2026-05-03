from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from kj_atlas_api.main import app
from kj_atlas_api.models_context import build_bundle as real_build_bundle
from kj_atlas_api.settings import settings


def _query_payload() -> dict:
    return {
        "queryId": "q-ce1-1",
        "goal": "find stable context",
        "scope": "document",
        "depth": 2,
        "constraints": {"islandIds": ["island-1"], "tags": {"priority": "high"}},
        "reviewFilter": "reviewedOnly",
        "safeModePolicy": "strict",
        "outputMode": "summary",
        "previewConfirmed": True,
    }


def _bundle_payload() -> dict:
    return {"query": _query_payload(), "stubDatasetId": "A2-minimal-v1"}


def _fixture_bundle_payload() -> dict:
    fixture_path = Path(__file__).parent / "fixtures" / "ce1_context_bundle_a2_minimal_v1.json"
    return json.loads(fixture_path.read_text(encoding="utf-8"))


def test_context_query_preview_required_when_not_confirmed() -> None:
    original_api_key = settings.api_key
    settings.api_key = None
    try:
        with TestClient(app) as client:
            payload = _query_payload()
            payload["previewConfirmed"] = False
            response = client.post("/context/query", json=payload)
            assert response.status_code == 422
            assert response.json()["detail"]["code"] == "preview_required"
    finally:
        settings.api_key = original_api_key


def test_context_query_rejects_unknown_contract_key() -> None:
    original_api_key = settings.api_key
    settings.api_key = None
    try:
        with TestClient(app) as client:
            payload = _query_payload()
            payload["unexpectedV1Key"] = "nope"
            response = client.post("/context/query", json=payload)
            assert response.status_code == 400
            assert response.json()["detail"]["code"] == "unknown_contract_key"
    finally:
        settings.api_key = original_api_key


def test_context_query_rejects_invalid_depth_boundary() -> None:
    original_api_key = settings.api_key
    settings.api_key = None
    try:
        with TestClient(app) as client:
            payload = _query_payload()
            payload["depth"] = 6
            response = client.post("/context/query", json=payload)
            assert response.status_code == 400
            detail = response.json()["detail"]
            assert isinstance(detail, list)
            assert any(error.get("loc") == ["depth"] or error.get("loc") == ("depth",) for error in detail)
    finally:
        settings.api_key = original_api_key


def test_context_bundle_rejects_unknown_contract_key() -> None:
    original_api_key = settings.api_key
    settings.api_key = None
    try:
        with TestClient(app) as client:
            payload = _bundle_payload()
            payload["unexpectedV1Key"] = "nope"
            response = client.post("/context/bundle", json=payload)
            assert response.status_code == 400
            assert response.json()["detail"]["code"] == "unknown_contract_key"
    finally:
        settings.api_key = original_api_key


def test_context_bundle_rejects_unknown_stub_dataset_id() -> None:
    original_api_key = settings.api_key
    settings.api_key = None
    try:
        with TestClient(app) as client:
            payload = _bundle_payload()
            payload["stubDatasetId"] = "A2-unknown"
            response = client.post("/context/bundle", json=payload)
            assert response.status_code == 400
            detail = response.json()["detail"]
            assert isinstance(detail, list)
            assert any(error.get("loc") == ["stubDatasetId"] or error.get("loc") == ("stubDatasetId",) for error in detail)
    finally:
        settings.api_key = original_api_key


def test_context_hashes_are_deterministic_for_same_canonical_query() -> None:
    original_api_key = settings.api_key
    settings.api_key = None
    try:
        with TestClient(app) as client:
            query_payload = _query_payload()
            bundle_payload = _bundle_payload()

            query_hashes = [client.post("/context/query", json=query_payload).json()["queryCanonicalHash"] for _ in range(3)]
            bundle_hashes = [client.post("/context/bundle", json=bundle_payload).json()["bundleHash"] for _ in range(3)]

            assert len(set(query_hashes)) == 1
            assert len(set(bundle_hashes)) == 1
    finally:
        settings.api_key = original_api_key


def test_context_bundle_preview_required_when_not_confirmed() -> None:
    original_api_key = settings.api_key
    settings.api_key = None
    try:
        with TestClient(app) as client:
            payload = _bundle_payload()
            payload["query"]["previewConfirmed"] = False
            response = client.post("/context/bundle", json=payload)
            assert response.status_code == 422
            assert response.json()["detail"]["code"] == "preview_required"
    finally:
        settings.api_key = original_api_key


def test_context_bundle_downstream_source_hash_comparable() -> None:
    original_api_key = settings.api_key
    settings.api_key = None
    try:
        with TestClient(app) as client:
            response = client.post("/context/bundle", json=_bundle_payload())
            assert response.status_code == 200
            body = response.json()
            assert isinstance(body["bundleHash"], str)
            assert len(body["bundleHash"]) == 64
    finally:
        settings.api_key = original_api_key


def test_context_bundle_strict_safemode_filters_unreviewed_even_when_included() -> None:
    original_api_key = settings.api_key
    settings.api_key = None
    try:
        with TestClient(app) as client:
            payload = _bundle_payload()
            payload["query"]["reviewFilter"] = "includeUnreviewed"
            response = client.post("/context/bundle", json=payload)
            assert response.status_code == 200
            body = response.json()
            assert body["reviewFlags"]["unreviewed"] == 0
            assert all(item["reviewed"] is True for item in body["selected"])
            assert "safe_mode_unreviewed_text" in body["excludedReason"]
    finally:
        settings.api_key = original_api_key


def test_context_resolve_route_contract_paths_are_unique() -> None:
    routes = [
        (route.path, ",".join(sorted(route.methods)))
        for route in app.router.routes
        if getattr(route, "path", None) in {"/context/bundles:resolve", "/context/v1/bundles:resolve"}
    ]
    assert routes.count(("/context/bundles:resolve", "POST")) == 1
    assert routes.count(("/context/v1/bundles:resolve", "POST")) == 1


def test_context_bundle_returns_409_when_bundle_hash_is_nondeterministic(monkeypatch) -> None:
    from kj_atlas_api import routes as routes_pkg

    def _tampered_build_bundle(request):
        response = real_build_bundle(request)
        return response.model_copy(update={"bundleHash": "f" * 64})

    original_api_key = settings.api_key
    settings.api_key = None
    monkeypatch.setattr(routes_pkg.context, "build_bundle", _tampered_build_bundle)
    try:
        with TestClient(app) as client:
            response = client.post("/context/bundle", json=_bundle_payload())
            assert response.status_code == 409
            assert response.json()["detail"]["code"] == "nondeterministic_bundle"
    finally:
        settings.api_key = original_api_key


def test_context_resolve_bundle_requires_safe_mode_enabled() -> None:
    original_api_key = settings.api_key
    settings.api_key = None
    try:
        with TestClient(app) as client:
            payload = {
                "query": "ce4 resolve",
                "dryRun": True,
                "sourceBundleHash": "mock:" + "a" * 64,
                "safeMode": False,
            }
            response = client.post("/context/bundles:resolve", json=payload)
            assert response.status_code == 422
            assert response.json()["detail"]["code"] == "safe_mode_required"
    finally:
        settings.api_key = original_api_key


def test_context_resolve_bundle_returns_contract_context_decision_consequences() -> None:
    original_api_key = settings.api_key
    settings.api_key = None
    try:
        with TestClient(app) as client:
            payload = {
                "query": "ce4 resolve",
                "dryRun": True,
                "sourceBundleHash": "sha256:" + "b" * 64,
                "safeMode": True,
            }
            response = client.post("/context/v1/bundles:resolve", json=payload)
            assert response.status_code == 200
            body = response.json()
            # Context
            assert isinstance(body["queryCanonicalHash"], str) and len(body["queryCanonicalHash"]) == 64
            # Decision
            assert body["proposalLifecycle"] == "proposed"
            assert body["sideEffect"] == "none"
            # Consequences
            assert body["auditChain"]["query"].startswith("query:")
            assert body["auditChain"]["bundle"].startswith("bundle:")
            assert body["auditChain"]["proposal"].startswith("proposal:")
            assert body["auditChain"]["apply"].startswith("apply:")
    finally:
        settings.api_key = original_api_key


def test_context_resolve_bundle_v1_alias_returns_identical_payload() -> None:
    original_api_key = settings.api_key
    settings.api_key = None
    try:
        with TestClient(app) as client:
            payload = {
                "query": "ce4 resolve alias parity",
                "dryRun": True,
                "sourceBundleHash": "sha256:" + "c" * 64,
                "safeMode": True,
            }
            latest_response = client.post("/context/bundles:resolve", json=payload)
            versioned_response = client.post("/context/v1/bundles:resolve", json=payload)

            assert latest_response.status_code == 200
            assert versioned_response.status_code == 200
            assert latest_response.json() == versioned_response.json()
    finally:
        settings.api_key = original_api_key


def test_context_bundle_fixture_contract_is_deterministic_3_of_3() -> None:
    original_api_key = settings.api_key
    settings.api_key = None
    try:
        with TestClient(app) as client:
            payload = _fixture_bundle_payload()
            responses = [client.post("/context/bundle", json=payload) for _ in range(3)]
            assert all(response.status_code == 200 for response in responses)
            hashes = [response.json()["bundleHash"] for response in responses]
            assert len(set(hashes)) == 1
    finally:
        settings.api_key = original_api_key


def test_context_bundle_rejects_unknown_nested_query_contract_key() -> None:
    original_api_key = settings.api_key
    settings.api_key = None
    try:
        with TestClient(app) as client:
            payload = _fixture_bundle_payload()
            payload["query"]["unexpectedNestedKey"] = "nope"
            response = client.post("/context/bundle", json=payload)
            assert response.status_code == 400
            assert response.json()["detail"]["code"] == "unknown_contract_key"
    finally:
        settings.api_key = original_api_key
