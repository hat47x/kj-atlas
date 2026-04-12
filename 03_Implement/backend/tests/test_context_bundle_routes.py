from __future__ import annotations

from fastapi.testclient import TestClient

from kj_atlas_api.main import app
from kj_atlas_api.settings import settings


def _doc_payload() -> dict:
    return {
        "version": 2,
        "id": "doc-ce1",
        "createdAt": "2026-04-01T00:00:00Z",
        "updatedAt": "2026-04-01T00:00:00Z",
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
        "cards": [
            {"id": "c-reviewed", "text": "reviewed body", "x": 0, "y": 0, "textReviewed": True},
            {"id": "c-unreviewed", "text": "unreviewed body", "x": 1, "y": 1, "textReviewed": False},
        ],
        "edges": [],
        "islands": [],
    }


def _query_payload() -> dict:
    return {
        "queryId": "q-ce1-1",
        "targetCardIds": ["c-reviewed", "c-unreviewed"],
        "depth": 1,
        "scope": "selection",
        "reviewedOnly": True,
        "safeMode": True,
    }


def test_context_query_missing_required_field_is_400() -> None:
    original_api_key = settings.api_key
    settings.api_key = None
    try:
        with TestClient(app) as client:
            invalid = _query_payload()
            invalid.pop("targetCardIds")
            response = client.post("/context/query", json=invalid)
            assert response.status_code == 400
    finally:
        settings.api_key = original_api_key


def test_context_bundle_hash_is_deterministic_for_same_query() -> None:
    original_api_key = settings.api_key
    settings.api_key = None
    try:
        with TestClient(app) as client:
            payload = {"query": _query_payload(), "doc": _doc_payload()}
            hashes = [client.post("/context/bundle", json=payload).json()["bundleHash"] for _ in range(10)]
            assert len(set(hashes)) == 1
    finally:
        settings.api_key = original_api_key


def test_context_bundle_hash_is_stable_when_query_id_changes() -> None:
    original_api_key = settings.api_key
    settings.api_key = None
    try:
        with TestClient(app) as client:
            payload_1 = {"query": _query_payload(), "doc": _doc_payload()}

            payload_2 = {"query": _query_payload(), "doc": _doc_payload()}
            payload_2["query"]["queryId"] = "q-ce1-2"

            hash_1 = client.post("/context/bundle", json=payload_1).json()["bundleHash"]
            hash_2 = client.post("/context/bundle", json=payload_2).json()["bundleHash"]

            assert hash_1 == hash_2
    finally:
        settings.api_key = original_api_key


def test_context_bundle_hash_is_stable_when_card_order_changes() -> None:
    original_api_key = settings.api_key
    settings.api_key = None
    try:
        with TestClient(app) as client:
            payload_1 = {"query": _query_payload(), "doc": _doc_payload()}

            reordered_doc = _doc_payload()
            reordered_doc["cards"] = list(reversed(reordered_doc["cards"]))
            payload_2 = {"query": _query_payload(), "doc": reordered_doc}

            hash_1 = client.post("/context/bundle", json=payload_1).json()["bundleHash"]
            hash_2 = client.post("/context/bundle", json=payload_2).json()["bundleHash"]

            assert hash_1 == hash_2
    finally:
        settings.api_key = original_api_key


def test_context_bundle_safe_mode_and_reviewed_filter_excludes_unreviewed_text() -> None:
    original_api_key = settings.api_key
    settings.api_key = None
    try:
        with TestClient(app) as client:
            payload = {"query": _query_payload(), "doc": _doc_payload()}
            response = client.post("/context/bundle", json=payload)
            assert response.status_code == 200
            bundle = response.json()["bundle"]
            assert bundle["selectedCards"] == [{"id": "c-reviewed", "text": "reviewed body", "reviewed": True}]
            assert {"cardId": "c-unreviewed", "reason": "reviewed_only_filter"} in bundle["excludedReasons"]
    finally:
        settings.api_key = original_api_key


def test_mock_integration_query_to_bundle_round_trip() -> None:
    original_api_key = settings.api_key
    settings.api_key = None
    try:
        with TestClient(app) as client:
            query_response = client.post("/context/query", json=_query_payload())
            assert query_response.status_code == 200
            validated = query_response.json()["query"]

            bundle_response = client.post("/context/bundle", json={"query": validated, "doc": _doc_payload()})
            assert bundle_response.status_code == 200
            assert bundle_response.json()["bundle"]["queryId"] == "q-ce1-1"
    finally:
        settings.api_key = original_api_key
