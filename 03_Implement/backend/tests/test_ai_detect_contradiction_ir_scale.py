"""Scale regression for detect-contradiction focus preservation.

AI-IR-FOCUS-PRESERVATION-01: the explicitly requested pair is route-required
meaning. A global IR cap must not make a human-confirmed/held contradiction look
new again merely because the pair sits outside the ordinary centrality cut.
"""

from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

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


def _card(index: int) -> dict:
    return {
        "id": f"c{index:03d}",
        "text": f"観察 c{index:03d}",
        "x": float(index % 30),
        "y": float(index // 30),
        "textReviewed": True,
    }


def _doc(state: str) -> dict:
    return {
        "version": 1,
        "id": "detect-focus-scale",
        "createdAt": "2026-09-03T00:00:00Z",
        "updatedAt": "2026-09-03T00:00:00Z",
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
        "cards": [_card(i) for i in range(300)],
        "edges": [],
        "islands": [],
        "evidenceLinks": [
            {
                "id": "ev-tail",
                "type": "contradicts",
                "fromCardId": "c298",
                "toCardId": "c299",
                "contradictionState": state,
            }
        ],
    }


def _payload(state: str) -> dict:
    return {
        "cardA": {
            "id": "c298",
            "text": "観察 c298",
            "textReviewed": True,
        },
        "cardB": {
            "id": "c299",
            "text": "観察 c299",
            "textReviewed": True,
        },
        "doc": _doc(state),
    }


@pytest.mark.parametrize("state", ["confirmed", "held"])
def test_adjudicated_tail_pair_is_preserved_and_not_reproposed(state: str) -> None:
    with TestClient(app) as client:
        response = client.post("/ai/detect-contradiction", json=_payload(state))

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["hasContradiction"] is False
    assert body["alreadyRecorded"] is True
    assert body["existingContradictionState"] == state
    assert _CAPTURED == []


@pytest.mark.parametrize("state", ["unconfirmed", "resolved"])
def test_unadjudicated_tail_pair_reaches_llm_with_focus_context(state: str) -> None:
    with TestClient(app) as client:
        response = client.post("/ai/detect-contradiction", json=_payload(state))

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["hasContradiction"] is True
    assert body["alreadyRecorded"] is False
    assert len(_CAPTURED) == 1

    ir = _CAPTURED[0].inputs
    assert ir is not None
    projected_ids = {card["id"] for card in ir["cards"]}
    assert {"c298", "c299"} <= projected_ids
    assert len(ir["cards"]) == 200
    assert ir["evidence_links"] == [
        {
            "id": "ev-tail",
            "type": "contradicts",
            "from_card_id": "c298",
            "to_card_id": "c299",
            "contradiction_state": state,
        }
    ]
    assert ir["truncation"] == {
        "truncated": True,
        "reason_codes": ["MAX_CARDS"],
    }
    assert f"contradictionState={state}" in _CAPTURED[0].prompt


def test_scale_failure_does_not_echo_focus_text_or_ids() -> None:
    body = _payload("held")
    body["doc"]["cards"] = body["doc"]["cards"][:-1]

    with TestClient(app) as client:
        response = client.post("/ai/detect-contradiction", json=body)

    # cardB travels outside doc and is deliberately added to the projection
    # source by the route, so a missing document member remains supported.
    assert response.status_code == 200, response.text
    assert response.json()["alreadyRecorded"] is False
    assert len(_CAPTURED) == 1
    detail = json.dumps(response.json(), ensure_ascii=False)
    assert "required_card_missing" not in detail
