from fastapi.testclient import TestClient

from kj_atlas_api.main import app
from kj_atlas_api.routes import ai_relations
from kj_atlas_api.settings import settings


class _StubProvider:
    def __init__(self, raw_text: str):
        self._raw_text = raw_text

    def generate(self, req):
        return type("Resp", (), {"raw_text": self._raw_text})()


def _payload() -> dict:
    return {
        "doc": {
            "version": 1,
            "id": "doc-1",
            "createdAt": "2026-02-11T00:00:00Z",
            "updatedAt": "2026-02-11T00:00:00Z",
            "transform": {"panX": 0, "panY": 0, "zoom": 1},
            "cards": [
                {"id": "c1", "text": "alpha", "x": 0, "y": 0},
                {"id": "c2", "text": "beta", "x": 10, "y": 10},
            ],
            "edges": [{"id": "e1", "fromId": "c1", "toId": "c2", "type": "related"}],
            "islands": [
                {"id": "i1", "cardIds": ["c1"]},
                {"id": "i2", "cardIds": ["c2"]},
            ],
        },
        "islandAId": "i1",
        "islandBId": "i2",
        "relationType": "related",
        "derived": False,
        "groundingCardIds": ["c1", "c2"],
        "groundingEdgeIds": ["e1"],
        "cardTexts": [
            {"id": "c1", "text": "alpha"},
            {"id": "c2", "text": "beta"},
        ],
        "edgeTexts": [{"edgeId": "e1", "type": "related", "from": "c1", "to": "c2"}],
    }


def test_summarize_relation_rejects_invalid_request_with_422() -> None:
    original_api_key = settings.api_key
    settings.api_key = None
    try:
        with TestClient(app) as client:
            invalid = _payload()
            invalid.pop("cardTexts")
            response = client.post("/ai/summarize-island-relation", json=invalid)
            assert response.status_code == 422
    finally:
        settings.api_key = original_api_key


def test_summarize_relation_rejects_non_subset_grounding_ids_with_422() -> None:
    original_api_key = settings.api_key
    original_generate = ai_relations.generate_with_fallback
    settings.api_key = None
    ai_relations.generate_with_fallback = lambda req: _StubProvider(
        '{"text":"draft","groundingCardIds":["not-allowed"],"groundingEdgeIds":[],"warnings":[]}'
    ).generate(req)

    try:
        with TestClient(app) as client:
            response = client.post("/ai/summarize-island-relation", json=_payload())
            assert response.status_code == 422
    finally:
        ai_relations.generate_with_fallback = original_generate
        settings.api_key = original_api_key
