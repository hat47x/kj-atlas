from fastapi.testclient import TestClient

from kj_atlas_api.main import app
from kj_atlas_api.routes import ai


def _payload() -> dict:
    return {
        "doc": {
            "version": 2,
            "id": "doc-1",
            "createdAt": "2026-02-11T00:00:00Z",
            "updatedAt": "2026-02-11T00:00:00Z",
            "transform": {"panX": 0, "panY": 0, "zoom": 1},
            "cards": [
                {"id": "c1", "text": "alpha", "x": 0, "y": 0},
                {"id": "c2", "text": "beta", "x": 10, "y": 10},
            ],
            "edges": [],
            "islands": [{"id": "i1", "cardIds": ["c1", "c2"], "summaryText": "old summary"}],
        },
        "islandId": "i1",
        "sourceBundleHash": "a" * 64,
    }


def test_propose_island_summary_returns_proposal_without_auto_apply() -> None:
    original_generate = ai.generate_with_fallback

    class _StubResponse:
        raw_text = '{"summaryText":"new summary","groundingIds":["c1"]}'

    ai.generate_with_fallback = lambda _: _StubResponse()
    try:
        with TestClient(app) as client:
            response = client.post("/ai/proposals/island-summary", json=_payload())
    finally:
        ai.generate_with_fallback = original_generate
    assert response.status_code == 200
    body = response.json()
    assert body["proposalId"].startswith("proposal-")
    assert body["status"] == "proposed"
    assert body["reviewState"] == "unreviewed"
    assert body["sourceBundleHash"] == "a" * 64
    assert body["diff"]["before"] == "old summary"
    assert isinstance(body["diff"]["after"], str) and body["diff"]["after"].strip() != ""


def test_record_proposal_decision_maps_to_lifecycle_status_without_review_promotion() -> None:
    expected = {
        "adopt": "accepted",
        "accepted": "accepted",
        "reject": "rejected",
        "rejected": "rejected",
        "hold": "held",
        "held": "held",
    }
    with TestClient(app) as client:
        for decision, expected_status in expected.items():
            response = client.post(
                "/ai/proposals/audit",
                json={"proposalId": "proposal-1", "decision": decision, "actor": "tester"},
            )
            assert response.status_code == 200
            assert response.json()["status"] == expected_status
            assert response.json()["reviewState"] == "unreviewed"


def test_propose_island_summary_rejects_invalid_source_bundle_hash() -> None:
    payload = _payload()
    payload["sourceBundleHash"] = "invalid-hash"
    with TestClient(app) as client:
        response = client.post("/ai/proposals/island-summary", json=payload)
    assert response.status_code == 422
