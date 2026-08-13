"""SEC-AI-SAFEMODE-01 (ADR-0068 D2=B): unreviewed card text is rejected at the
AI endpoint boundary unless the caller explicitly relaxes and the profile
permits it."""

from __future__ import annotations

from fastapi.testclient import TestClient

from kj_atlas_api.main import app
from kj_atlas_api.routes import ai
from kj_atlas_api.settings import settings


def _doc_with_cards(cards: list[dict]) -> dict:
    return {
        "version": 1,
        "id": "safemode-doc",
        "createdAt": "2026-02-11T00:00:00Z",
        "updatedAt": "2026-02-11T00:00:00Z",
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
        "cards": cards,
        "edges": [],
        "islands": [{"id": "i1", "cardIds": [c["id"] for c in cards], "summaryText": "s"}],
    }


def _stub_generate(_req):
    return type("R", (), {"raw_text": '{"summaryText":"new","groundingIds":["c1"]}'})()


def test_rejects_unreviewed_text_by_default(monkeypatch) -> None:
    monkeypatch.setattr(ai, "generate_with_fallback", _stub_generate)
    monkeypatch.setattr(settings, "allow_unreviewed_ai_text", False)
    doc = _doc_with_cards([{"id": "c1", "text": "alpha", "x": 0, "y": 0}])  # textReviewed missing
    with TestClient(app) as client:
        resp = client.post("/ai/suggest-island-summary", json={"doc": doc, "islandId": "i1"})
    assert resp.status_code == 422
    assert resp.json()["detail"]["code"] == "unreviewed_text_not_allowed"


def test_accepts_reviewed_text(monkeypatch) -> None:
    monkeypatch.setattr(ai, "generate_with_fallback", _stub_generate)
    doc = _doc_with_cards([{"id": "c1", "text": "alpha", "x": 0, "y": 0, "textReviewed": True}])
    with TestClient(app) as client:
        resp = client.post("/ai/suggest-island-summary", json={"doc": doc, "islandId": "i1"})
    assert resp.status_code == 200


def test_relaxation_requires_profile_permission(monkeypatch) -> None:
    monkeypatch.setattr(ai, "generate_with_fallback", _stub_generate)
    # request asks to relax, but the profile forbids it -> still rejected
    monkeypatch.setattr(settings, "allow_unreviewed_ai_text", False)
    doc = _doc_with_cards([{"id": "c1", "text": "alpha", "x": 0, "y": 0}])
    with TestClient(app) as client:
        resp = client.post(
            "/ai/suggest-island-summary",
            json={"doc": doc, "islandId": "i1", "allowUnreviewedText": True},
        )
    assert resp.status_code == 422


def test_relaxation_honored_when_profile_allows(monkeypatch) -> None:
    monkeypatch.setattr(ai, "generate_with_fallback", _stub_generate)
    monkeypatch.setattr(settings, "allow_unreviewed_ai_text", True)
    doc = _doc_with_cards([{"id": "c1", "text": "alpha", "x": 0, "y": 0}])
    with TestClient(app) as client:
        resp = client.post(
            "/ai/suggest-island-summary",
            json={"doc": doc, "islandId": "i1", "allowUnreviewedText": True},
        )
    assert resp.status_code == 200
