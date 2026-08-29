"""Integration tests for `/ai/detect-contradiction` on the LLM input IR path.

Stage 1 of the `ADR-0069` rollout (`AI-IR-PROJECTION-01`). Two things are being
proven here:

1. AC-1 -- the endpoint receives `evidenceLinks` / `contradictionState` and no
   longer re-surfaces a contradiction a human already confirmed or held.
2. The pre-existing SafeMode gate (`_reject_unreviewed_cards`, shipped by
   `SEC-AI-SAFEMODE-01` / ADR-0068) is UNCHANGED. The IR's own check is an
   additional layer, not a replacement -- so both must be observable.
"""
from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from kj_atlas_api.llm_input_ir import IR_VERSION
from kj_atlas_api.main import app
from kj_atlas_api.routes import ai
from kj_atlas_api.settings import settings

_CAPTURED: list = []


def _stub_generate(req):
    _CAPTURED.append(req)
    return type("R", (), {"raw_text": '{"hasContradiction": true, "explanation": "e"}'})()


@pytest.fixture(autouse=True)
def _stub_llm(monkeypatch: pytest.MonkeyPatch):
    _CAPTURED.clear()
    monkeypatch.setattr(ai, "generate_with_fallback", _stub_generate)
    monkeypatch.setattr(settings, "allow_unreviewed_ai_text", False)
    yield
    _CAPTURED.clear()


def _doc(*, evidence: list[dict] | None = None, edges: list[dict] | None = None) -> dict:
    return {
        "version": 1,
        "id": "contradiction-doc",
        "createdAt": "2026-08-30T00:00:00Z",
        "updatedAt": "2026-08-30T00:00:00Z",
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
        "cards": [
            {
                "id": "c-remote",
                "text": "チームは在宅勤務でも成果を出せると考えている",
                "x": 0,
                "y": 0,
                "textReviewed": True,
            },
            {
                "id": "c-office",
                "text": "対面でないと設計の議論が浅くなると感じている",
                "x": 40,
                "y": 0,
                "textReviewed": True,
            },
        ],
        "edges": edges or [],
        "islands": [
            {
                "id": "isl-work",
                "cardIds": ["c-remote", "c-office"],
                "title": "働く場所をめぐる見立てが割れている",
                "titleReviewed": True,
            }
        ],
        "evidenceLinks": evidence or [],
    }


def _payload(doc: dict | None = None) -> dict:
    body = {
        "cardA": {
            "id": "c-remote",
            "text": "チームは在宅勤務でも成果を出せると考えている",
            "textReviewed": True,
        },
        "cardB": {
            "id": "c-office",
            "text": "対面でないと設計の議論が浅くなると感じている",
            "textReviewed": True,
        },
    }
    if doc is not None:
        body["doc"] = doc
    return body


def _evidence(state: str, link_id: str = "ev1") -> dict:
    return {
        "id": link_id,
        "type": "contradicts",
        "fromCardId": "c-remote",
        "toCardId": "c-office",
        "contradictionState": state,
    }


# ---------------------------------------------------------------------------
# AC-1: an adjudicated contradiction is not re-proposed
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("state", ["confirmed", "held"])
def test_adjudicated_contradiction_is_not_resurfaced(state: str) -> None:
    with TestClient(app) as client:
        resp = client.post(
            "/ai/detect-contradiction", json=_payload(_doc(evidence=[_evidence(state)]))
        )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["hasContradiction"] is False
    assert body["alreadyRecorded"] is True
    assert body["existingContradictionState"] == state
    # The decision is answered from the IR; the model is never asked again.
    assert _CAPTURED == []


@pytest.mark.parametrize("state", ["unconfirmed", "resolved"])
def test_unadjudicated_states_still_reach_the_model(state: str) -> None:
    with TestClient(app) as client:
        resp = client.post(
            "/ai/detect-contradiction", json=_payload(_doc(evidence=[_evidence(state)]))
        )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["hasContradiction"] is True
    assert body["alreadyRecorded"] is False
    assert len(_CAPTURED) == 1


def test_reverse_direction_link_also_suppresses() -> None:
    """The pair is unordered: B->A `confirmed` is the same human decision."""
    link = _evidence("confirmed")
    link["fromCardId"], link["toCardId"] = link["toCardId"], link["fromCardId"]
    with TestClient(app) as client:
        resp = client.post("/ai/detect-contradiction", json=_payload(_doc(evidence=[link])))
    assert resp.json()["alreadyRecorded"] is True
    assert _CAPTURED == []


def test_confirmed_link_between_other_cards_does_not_suppress() -> None:
    doc = _doc(evidence=[_evidence("confirmed")])
    doc["cards"].append(
        {"id": "c-third", "text": "評価制度の見直しは着手していない", "x": 80, "y": 0, "textReviewed": True}
    )
    body = _payload(doc)
    body["cardB"] = {
        "id": "c-third",
        "text": "評価制度の見直しは着手していない",
        "textReviewed": True,
    }
    with TestClient(app) as client:
        resp = client.post("/ai/detect-contradiction", json=body)
    assert resp.json()["alreadyRecorded"] is False
    assert len(_CAPTURED) == 1


# ---------------------------------------------------------------------------
# The IR actually reaches the LLM boundary
# ---------------------------------------------------------------------------


def test_request_carries_the_ir_and_the_prompt_shows_the_context() -> None:
    doc = _doc(
        evidence=[_evidence("unconfirmed")],
        edges=[{"id": "e1", "fromId": "c-remote", "toId": "c-office", "type": "negate"}],
    )
    with TestClient(app) as client:
        resp = client.post("/ai/detect-contradiction", json=_payload(doc))
    assert resp.status_code == 200, resp.text

    llm_request = _CAPTURED[0]
    ir = llm_request.inputs
    assert ir is not None
    assert ir["ir_version"] == IR_VERSION
    # ADR-0069 D1=B: this endpoint does not request coordinates.
    assert "coordinates" not in ir
    assert ir["relations"] == [
        {"id": "negate:c-remote:c-office", "from": "c-remote", "to": "c-office", "type": "negate"}
    ]
    assert ir["islands"][0]["id"] == "isl-work"
    assert ir["evidence_links"][0]["contradiction_state"] == "unconfirmed"
    assert ir["graph_summary"]["contradiction_subgraphs"][0]["subgraph_id"] == "neg-001"

    prompt = llm_request.prompt
    assert "contradictionState=unconfirmed" in prompt
    assert "negate: c-remote -> c-office" in prompt
    assert "isl-work" in prompt
    assert "reviewState=human_reviewed" in prompt


def test_two_card_request_without_doc_still_works() -> None:
    """AC-11 (narrowed): the shipped request shape keeps working."""
    with TestClient(app) as client:
        resp = client.post("/ai/detect-contradiction", json=_payload())
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["hasContradiction"] is True
    assert body["alreadyRecorded"] is False

    ir = _CAPTURED[0].inputs
    assert ir["ir_version"] == IR_VERSION
    assert [card["id"] for card in ir["cards"]] == ["c-office", "c-remote"]
    assert ir["relations"] == []
    assert "islands" not in ir
    assert "created_at" not in ir["meta"]  # never invented (spec §2.4 rule 5)


def test_response_shape_is_backward_compatible() -> None:
    with TestClient(app) as client:
        resp = client.post("/ai/detect-contradiction", json=_payload())
    body = resp.json()
    assert set(body) == {
        "hasContradiction",
        "explanation",
        "alreadyRecorded",
        "existingContradictionState",
    }
    assert isinstance(body["hasContradiction"], bool)


# ---------------------------------------------------------------------------
# SafeMode: layer 1 unchanged, layer 2 added
# ---------------------------------------------------------------------------


def test_existing_reject_unreviewed_cards_behaviour_is_unchanged() -> None:
    """Regression proof for SEC-AI-SAFEMODE-01/02: the shipped 422 still fires,
    with the same code, and still fires BEFORE any LLM call."""
    with TestClient(app) as client:
        # unspecified textReviewed -> fail-closed (ADR-0068 D3=A)
        resp = client.post(
            "/ai/detect-contradiction",
            json={
                "cardA": {"id": "c1", "text": "alpha"},
                "cardB": {"id": "c2", "text": "beta"},
            },
        )
        assert resp.status_code == 422
        assert resp.json()["detail"]["code"] == "unreviewed_text_not_allowed"

        # a single unreviewed card still poisons the pair
        resp = client.post(
            "/ai/detect-contradiction",
            json={
                "cardA": {"id": "c1", "text": "alpha", "textReviewed": True},
                "cardB": {"id": "c2", "text": "beta", "textReviewed": False},
            },
        )
        assert resp.status_code == 422
        assert resp.json()["detail"]["code"] == "unreviewed_text_not_allowed"
    assert _CAPTURED == []


def test_route_level_gate_fires_even_when_the_document_is_clean() -> None:
    """The doc cards are reviewed but cardA is not: layer 1 must still reject."""
    body = _payload(_doc())
    body["cardA"]["textReviewed"] = False
    with TestClient(app) as client:
        resp = client.post("/ai/detect-contradiction", json=body)
    assert resp.status_code == 422
    assert resp.json()["detail"]["code"] == "unreviewed_text_not_allowed"
    assert _CAPTURED == []


def test_ir_layer_rejects_unreviewed_document_text_the_route_gate_cannot_see() -> None:
    """Layer 2 catches what layer 1 structurally cannot.

    `_reject_unreviewed_cards` only inspects cardA/cardB. An unreviewed card
    that arrives inside `doc` is invisible to it -- and the IR builder refuses
    it (llm_input_ir_spec.md §7.1).
    """
    doc = _doc()
    doc["cards"].append(
        {"id": "c-draft", "text": "まだ確認していない下書き", "x": 90, "y": 0}
    )
    with TestClient(app) as client:
        resp = client.post("/ai/detect-contradiction", json=_payload(doc))
    assert resp.status_code == 422
    assert resp.json()["detail"]["code"] == "unreviewed_text_not_allowed"
    assert _CAPTURED == []


def test_ir_layer_rejects_pii_in_document_text() -> None:
    doc = _doc()
    doc["cards"][0]["text"] = "連絡先は contact@example.com である"
    body = _payload(doc)
    body["cardA"]["text"] = "連絡先は contact@example.com である"
    with TestClient(app) as client:
        resp = client.post("/ai/detect-contradiction", json=body)
    assert resp.status_code == 422
    detail = resp.json()["detail"]
    assert detail["code"] == "pii_detected"
    # SEC-VALIDATION-LEAK-01: the rejected value is not reflected back.
    assert "contact@example.com" not in json.dumps(detail, ensure_ascii=False)
    assert _CAPTURED == []


def test_same_card_twice_is_rejected() -> None:
    body = _payload()
    body["cardB"] = dict(body["cardA"])
    with TestClient(app) as client:
        resp = client.post("/ai/detect-contradiction", json=body)
    assert resp.status_code == 422
    assert resp.json()["detail"]["code"] == "duplicate_card_id"
