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


# ---------------------------------------------------------------------------
# SEC-AI-SAFEMODE-02: the no-document AI routes take card text directly, so the
# review state travels with the request (`textReviewed`). Fail-closed default:
# an unspecified / false textReviewed is rejected (ADR-0068 D3=A).
# ---------------------------------------------------------------------------


def _stub_generate_by_task(req):
    task = req.task
    if task == "refine_card_text":
        raw = '{"refinedText": "（モック）改善案", "reasoning": "r"}'
    elif task == "suggest_card_groups":
        raw = '{"groups": [{"label": "A", "cardIds": ["c1", "c2"]}]}'
    elif task == "detect_contradiction":
        raw = '{"hasContradiction": false, "explanation": "e"}'
    else:
        raw = "{}"
    return type("R", (), {"raw_text": raw})()


_NO_DOC_CASES = [
    ("/ai/refine-card-text", {"cardText": "alpha"}),
    (
        "/ai/suggest-card-groups",
        {"cards": [{"id": "c1", "text": "alpha"}, {"id": "c2", "text": "beta"}]},
    ),
    (
        "/ai/detect-contradiction",
        {"cardA": {"id": "c1", "text": "alpha"}, "cardB": {"id": "c2", "text": "beta"}},
    ),
]


def test_nodoc_routes_reject_unreviewed_by_default(monkeypatch) -> None:
    """SEC-AI-SAFEMODE-02: unspecified textReviewed is fail-closed (unreviewed)."""
    monkeypatch.setattr(ai, "generate_with_fallback", _stub_generate_by_task)
    monkeypatch.setattr(settings, "allow_unreviewed_ai_text", False)
    with TestClient(app) as client:
        for path, payload in _NO_DOC_CASES:
            resp = client.post(path, json=payload)
            assert resp.status_code == 422, f"{path}: {resp.status_code} {resp.text}"
            assert resp.json()["detail"]["code"] == "unreviewed_text_not_allowed", path


def test_nodoc_routes_accept_reviewed_text(monkeypatch) -> None:
    monkeypatch.setattr(ai, "generate_with_fallback", _stub_generate_by_task)
    with TestClient(app) as client:
        resp = client.post("/ai/refine-card-text", json={"cardText": "alpha", "textReviewed": True})
        assert resp.status_code == 200, resp.text
        resp = client.post(
            "/ai/suggest-card-groups",
            json={
                "cards": [
                    {"id": "c1", "text": "alpha", "textReviewed": True},
                    {"id": "c2", "text": "beta", "textReviewed": True},
                ]
            },
        )
        assert resp.status_code == 200, resp.text
        resp = client.post(
            "/ai/detect-contradiction",
            json={
                "cardA": {"id": "c1", "text": "alpha", "textReviewed": True},
                "cardB": {"id": "c2", "text": "beta", "textReviewed": True},
            },
        )
        assert resp.status_code == 200, resp.text


def test_nodoc_routes_reject_when_any_card_unreviewed(monkeypatch) -> None:
    """A single unreviewed card poisons the request (detect-contradiction)."""
    monkeypatch.setattr(ai, "generate_with_fallback", _stub_generate_by_task)
    monkeypatch.setattr(settings, "allow_unreviewed_ai_text", False)
    with TestClient(app) as client:
        resp = client.post(
            "/ai/detect-contradiction",
            json={
                "cardA": {"id": "c1", "text": "alpha", "textReviewed": True},
                "cardB": {"id": "c2", "text": "beta"},  # unspecified -> unreviewed
            },
        )
    assert resp.status_code == 422
    assert resp.json()["detail"]["code"] == "unreviewed_text_not_allowed"


def test_nodoc_relaxation_requires_profile_permission(monkeypatch) -> None:
    monkeypatch.setattr(ai, "generate_with_fallback", _stub_generate_by_task)
    monkeypatch.setattr(settings, "allow_unreviewed_ai_text", False)
    with TestClient(app) as client:
        resp = client.post(
            "/ai/refine-card-text",
            json={"cardText": "alpha", "textReviewed": False, "allowUnreviewedText": True},
        )
    assert resp.status_code == 422


def test_nodoc_relaxation_honored_when_profile_allows(monkeypatch) -> None:
    monkeypatch.setattr(ai, "generate_with_fallback", _stub_generate_by_task)
    monkeypatch.setattr(settings, "allow_unreviewed_ai_text", True)
    with TestClient(app) as client:
        resp = client.post(
            "/ai/refine-card-text",
            json={"cardText": "alpha", "textReviewed": False, "allowUnreviewedText": True},
        )
    assert resp.status_code == 200
