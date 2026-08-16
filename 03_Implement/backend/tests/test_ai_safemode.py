"""SEC-AI-SAFEMODE-01 (ADR-0068 D2=B): unreviewed card text is rejected at the
AI endpoint boundary unless the caller explicitly relaxes and the profile
permits it."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from kj_atlas_api.main import app
from kj_atlas_api.routes import ai
from kj_atlas_api.settings import settings


@pytest.fixture(scope="module", autouse=True)
def _app_db_schema() -> None:
    """Ensure the shared SQLite DB has the full app schema (tenant_model_allowlist etc.)."""
    from kj_atlas_api.db import engine
    from kj_atlas_api.models import Base

    Base.metadata.create_all(bind=engine)


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
    elif task == "suggest_document_title":
        raw = '{"candidates": [{"title": "（モック）タイトル案"}]}'
    elif task == "summarize_island_relation":
        raw = '{"text": "（モック）関係の要約", "groundingCardIds": [], "groundingEdgeIds": [], "warnings": []}'
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


# ---------------------------------------------------------------------------
# SEC-AI-SAFEMODE-01/02 coverage canary: EVERY AI route that forwards card text
# to the LLM must reject an unreviewed payload with 422. A route added without
# joining this list is a boundary hole — the test fails until it is classified
# (either gated, or proven not to forward card text).
# ---------------------------------------------------------------------------


def _doc_with_cards_covered(cards: list[dict]) -> dict:
    return {
        "version": 1,
        "id": "coverage-doc",
        "createdAt": "2026-02-11T00:00:00Z",
        "updatedAt": "2026-02-11T00:00:00Z",
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
        "cards": [{**c, "x": c.get("x", 0), "y": c.get("y", 0)} for c in cards],
        "edges": [],
        "islands": [
            {
                "id": "i1",
                "cardIds": [c["id"] for c in cards],
                "summaryText": "s",
            }
        ],
    }


#: Every content-bearing AI route, with an UNREVIEWED payload. The gate must
#: fire (422) before any LLM call. Keep in sync when routes are added/removed.
_CONTENT_ROUTE_CASES = [
    # doc-context routes (SEC-AI-SAFEMODE-01): doc cards without textReviewed.
    ("/ai/suggest-layout", {"doc": _doc_with_cards_covered([{"id": "c1", "text": "a"}])}),
    ("/ai/suggest-merges", {"doc": _doc_with_cards_covered([{"id": "c1", "text": "a"}])}),
    (
        "/ai/suggest-island-summary",
        {"doc": _doc_with_cards_covered([{"id": "c1", "text": "a"}]), "islandId": "i1"},
    ),
    (
        "/ai/generate-narrative",
        {"doc": _doc_with_cards_covered([{"id": "c1", "text": "a"}])},
    ),
    (
        "/ai/check-narrative",
        {"doc": _doc_with_cards_covered([{"id": "c1", "text": "a"}]), "narrativeText": "n"},
    ),
    # NOTE: /ai/proposals/island-summary and /ai/proposals/opposing-viewpoint
    # are deliberately NOT in this list — they are CE4 proposal machinery that
    # requires a persisted document (404 otherwise), so their SafeMode gates are
    # exercised by the proposal-route tests (test_ce2_*, test_ai_oppose.py) and
    # by the business-flow E2E scenarios 9/16/18.
    (
        "/ai/summarize-island-relation",
        {
            "doc": _doc_with_cards_covered([{"id": "c1", "text": "a"}]),
            "islandAId": "i1",
            "islandBId": "i1",
            "relationType": "related",
            "derived": True,
            "groundingCardIds": [],
            "groundingEdgeIds": [],
            "cardTexts": [{"id": "c1", "text": "a"}],
        },
    ),
    # no-doc routes (SEC-AI-SAFEMODE-02): textReviewed defaults false.
    ("/ai/refine-card-text", {"cardText": "alpha"}),
    (
        "/ai/suggest-card-groups",
        {"cards": [{"id": "c1", "text": "alpha"}, {"id": "c2", "text": "beta"}]},
    ),
    (
        "/ai/detect-contradiction",
        {"cardA": {"id": "c1", "text": "alpha"}, "cardB": {"id": "c2", "text": "beta"}},
    ),
    ("/ai/suggest-document-title", {"islandTitles": [], "cardTexts": ["alpha"]}),
]


@pytest.mark.parametrize("path,payload", _CONTENT_ROUTE_CASES, ids=[c[0] for c in _CONTENT_ROUTE_CASES])
def test_every_content_ai_route_rejects_unreviewed_text(monkeypatch, path, payload) -> None:
    """Coverage canary: unreviewed text must be rejected at every content route.

    The 422 body's code asserts it is the SafeMode gate (not request validation),
    so a route that returns 422 for another reason fails here — forcing any newly
    added content route to be classified (gated or proven content-free)."""
    monkeypatch.setattr(ai, "generate_with_fallback", _stub_generate_by_task)
    monkeypatch.setattr(settings, "allow_unreviewed_ai_text", False)
    with TestClient(app) as client:
        resp = client.post(path, json=payload)
        assert resp.status_code == 422, f"{path}: {resp.status_code} {resp.text[:200]}"
        assert resp.json()["detail"]["code"] == "unreviewed_text_not_allowed", path


def test_newly_gated_routes_accept_reviewed_text(monkeypatch) -> None:
    """The two routes closed in iteration 48 accept reviewed content (200)."""
    from kj_atlas_api.routes import ai_relations

    monkeypatch.setattr(ai, "generate_with_fallback", _stub_generate_by_task)
    # ai_relations imports generate_with_fallback directly, so stub its module.
    monkeypatch.setattr(ai_relations, "generate_with_fallback", _stub_generate_by_task)
    with TestClient(app) as client:
        # suggest-document-title (no-doc, textReviewed certified).
        resp = client.post(
            "/ai/suggest-document-title",
            json={"islandTitles": ["島A"], "cardTexts": ["alpha"], "textReviewed": True},
        )
        assert resp.status_code == 200, resp.text
        # summarize-island-relation (doc-context, doc cards reviewed).
        doc = _doc_with_cards([{"id": "c1", "text": "alpha", "x": 0, "y": 0, "textReviewed": True}])
        resp = client.post(
            "/ai/summarize-island-relation",
            json={
                "doc": doc,
                "islandAId": "i1",
                "islandBId": "i1",
                "relationType": "related",
                "derived": True,
                "groundingCardIds": [],
                "groundingEdgeIds": [],
                "cardTexts": [{"id": "c1", "text": "alpha"}],
            },
        )
        assert resp.status_code == 200, resp.text
