from __future__ import annotations

from fastapi.testclient import TestClient

from kj_atlas_api.main import app
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
