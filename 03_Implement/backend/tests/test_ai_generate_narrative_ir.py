"""Integration tests for `/ai/generate-narrative` on the LLM input IR path.

Stage 3 of the `ADR-0069` rollout (`AI-IR-PROJECTION-01`), acceptance AC-3.
Four things are being proven here:

1. AC-3 -- the endpoint receives the `edges` of the document as the IR's typed
   `relations`, and `causal` / `negate` are actually present in what goes to the
   model: both in `LLMRequest.inputs` (the IR itself) and in the rendered
   prompt, as those two words, not folded into a generic "related" bucket.
2. The relations are placed ON the reading order, so the narrative can use them
   as joints rather than having to rediscover where in the sequence they act.
3. The pre-existing SafeMode gate (`_reject_unreviewed_text`, shipped by
   `SEC-AI-SAFEMODE-01` / ADR-0068) is UNCHANGED, and the IR's own check
   (llm_input_ir_spec.md §7.1) is an additional layer, not a replacement.
4. The shipped request/response contract is untouched (AC-11) -- there IS a
   frontend caller for this endpoint (`frontend/src/api/client.ts`
   `generateNarrative`), unlike stages 1-2 -- and the reading-order line format
   the mock adapter parses is byte-compatible.
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
_RESPONSE: dict = {}


def _stub_generate(req):
    _CAPTURED.append(req)
    return type("R", (), {"raw_text": json.dumps(_RESPONSE)})()


@pytest.fixture(autouse=True)
def _stub_llm(monkeypatch: pytest.MonkeyPatch):
    _CAPTURED.clear()
    _RESPONSE.clear()
    _RESPONSE["text"] = "（草稿・未レビュー）読み順に沿った解釈の下書きです。"
    _RESPONSE["basedOnReadingOrder"] = ["isl-budget", "isl-effect"]
    monkeypatch.setattr(ai, "generate_with_fallback", _stub_generate)
    # This module exercises the IR projection, not registry availability
    # (AI-MODEL-GOVERNANCE-02); `test_ai_model_governance.py` owns that gate.
    monkeypatch.setattr(ai, "_assert_model_allowed", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(settings, "allow_unreviewed_ai_text", False)
    yield
    _CAPTURED.clear()
    _RESPONSE.clear()


_TEXTS = {
    "c-budget": "市は補正予算を組み替えたと説明している",
    "c-cut": "現場の人員配置はさらに絞られると見ている",
    "c-oppose": "人員を絞っても現場は回ると考えている",
    "c-aside": "来年度の制度改正はまだ議論されていない",
}


def _card(card_id: str, x: int) -> dict:
    return {
        "id": card_id,
        "text": _TEXTS[card_id],
        "x": x,
        "y": 0,
        "textReviewed": True,
    }


def _doc() -> dict:
    """A document whose reading order has a causal pull and a negation inside it.

    `isl-budget` (1st) -> `isl-effect` (2nd); `c-budget --causal--> c-cut`
    crosses that boundary and `c-cut --negate--> c-oppose` sits inside the
    second item. `c-aside` is reachable by a `related` edge but is NOT in the
    reading order, which is the third placement case.
    """
    return {
        "version": 1,
        "id": "narrative-ir-doc",
        "createdAt": "2026-08-30T00:00:00Z",
        "updatedAt": "2026-08-30T00:00:00Z",
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
        "cards": [
            _card("c-budget", 0),
            _card("c-cut", 40),
            _card("c-oppose", 80),
            _card("c-aside", 120),
        ],
        "edges": [
            {"id": "e-causal", "fromId": "c-budget", "toId": "c-cut", "type": "causal"},
            {"id": "e-negate", "fromId": "c-cut", "toId": "c-oppose", "type": "negate"},
            {"id": "e-related", "fromId": "c-budget", "toId": "c-aside", "type": "related"},
            # spec §2.3 rule 6: excluded from the IR, not rejected.
            {"id": "e-unknown", "fromId": "c-budget", "toId": "c-oppose", "type": "unknown"},
            {
                "id": "e-island",
                "fromId": "isl-budget",
                "toId": "isl-effect",
                "fromKind": "island",
                "toKind": "island",
                "type": "causal",
            },
        ],
        "islands": [
            {
                "id": "isl-budget",
                "cardIds": ["c-budget"],
                "title": "予算の組み替えが起点になっている",
                "titleReviewed": True,
            },
            {
                "id": "isl-effect",
                "cardIds": ["c-cut", "c-oppose"],
                "title": "現場への影響の見立てが割れている",
            },
        ],
        "evidenceLinks": [
            {
                "id": "ev-1",
                "type": "contradicts",
                "fromCardId": "c-cut",
                "toCardId": "c-oppose",
                "contradictionState": "held",
            }
        ],
        "readingOrder": ["isl-budget", "isl-effect"],
    }


# ---------------------------------------------------------------------------
# AC-3: causal / negate actually reach the model
# ---------------------------------------------------------------------------


def test_ir_carries_the_causal_and_negate_edges_of_the_document() -> None:
    """The IR handed to the LLM boundary carries the typed relations (AC-3)."""
    with TestClient(app) as client:
        resp = client.post("/ai/generate-narrative", json={"doc": _doc()})
    assert resp.status_code == 200, resp.text

    ir = _CAPTURED[0].inputs
    assert ir is not None
    assert ir["ir_version"] == IR_VERSION
    # ADR-0069 D1=B / spec §2.2.1: this endpoint does not request coordinates.
    assert "coordinates" not in ir

    by_type = {relation["type"]: relation for relation in ir["relations"]}
    assert "causal" in by_type and "negate" in by_type
    assert (by_type["causal"]["from"], by_type["causal"]["to"]) == ("c-budget", "c-cut")
    assert (by_type["negate"]["from"], by_type["negate"]["to"]) == ("c-cut", "c-oppose")
    # ...and the rest of the five-value vocabulary is not dropped either.
    assert by_type["related"]["from"] == "c-budget"
    # spec §2.3 rule 6: an unknown type carries no structure and is excluded.
    assert "unknown" not in by_type
    # ...as are island-to-island edges (they belong to `islands`, Stage 4).
    assert all(
        relation["from"] not in {"isl-budget", "isl-effect"} for relation in ir["relations"]
    )


def test_prompt_names_the_causal_and_negate_relations() -> None:
    """AC-3, prompt side: the two types are present as themselves.

    A relation the model can only see as "related" is exactly the dilution the
    issue forbids, so the assertions are on the typed arrows.
    """
    with TestClient(app) as client:
        resp = client.post("/ai/generate-narrative", json={"doc": _doc()})
    assert resp.status_code == 200, resp.text

    prompt = _CAPTURED[0].prompt
    assert 'card "c-budget" --causal--> card "c-cut"' in prompt
    assert 'card "c-cut" --negate--> card "c-oppose"' in prompt
    assert 'card "c-budget" --related--> card "c-aside"' in prompt
    assert "Logical relations:" in prompt
    assert "causal, negation, evidence" in prompt


def test_prompt_places_causal_and_negate_on_the_reading_order() -> None:
    with TestClient(app) as client:
        client.post("/ai/generate-narrative", json={"doc": _doc()})
    prompt = _CAPTURED[0].prompt

    assert (
        '- reading-order 1 -> reading-order 2: card "c-budget" --causal--> card "c-cut"'
        in prompt
    )
    assert (
        '- within reading-order 2: card "c-cut" --negate--> card "c-oppose"' in prompt
    )
    # `related` is context, not a joint: it is listed above but not on the spine.
    assert "--related--> card \"c-aside\"" in prompt
    assert '- outside the reading order: card "c-budget" --related' not in prompt


def test_a_relation_outside_the_reading_order_is_labelled_as_such() -> None:
    doc = _doc()
    doc["edges"].append(
        {"id": "e-off", "fromId": "c-aside", "toId": "c-budget", "type": "causal"}
    )
    with TestClient(app) as client:
        client.post("/ai/generate-narrative", json={"doc": doc})
    prompt = _CAPTURED[0].prompt
    assert (
        '- reading-order 1 <-> outside the reading order: card "c-aside" '
        '--causal--> card "c-budget"' in prompt
    )


def test_reading_order_of_bare_cards_also_receives_the_relations() -> None:
    """The reading order may name cards instead of islands; both map to a slot."""
    doc = _doc()
    doc["readingOrder"] = ["c-budget", "c-cut"]
    _RESPONSE["basedOnReadingOrder"] = ["c-budget", "c-cut"]
    with TestClient(app) as client:
        resp = client.post("/ai/generate-narrative", json={"doc": doc})
    assert resp.status_code == 200, resp.text
    assert (
        '- reading-order 1 -> reading-order 2: card "c-budget" --causal--> card "c-cut"'
        in _CAPTURED[0].prompt
    )


def test_evidence_links_now_carry_the_human_adjudicated_state() -> None:
    """The IR's `evidence_links` add `contradictionState`, which the pre-IR
    prompt could not show (spec §2.2B)."""
    with TestClient(app) as client:
        client.post("/ai/generate-narrative", json={"doc": _doc()})
    prompt = _CAPTURED[0].prompt
    assert (
        'card "c-cut" --evidence:contradicts--> card "c-oppose" (contradictionState=held)'
        in prompt
    )


def test_island_to_island_edges_are_still_listed() -> None:
    """Regression: island edges are excluded from the IR by spec §2.3 rule 6,
    so they keep being read off the document. Wiring the IR in must not lose
    the context that shipped before."""
    with TestClient(app) as client:
        client.post("/ai/generate-narrative", json={"doc": _doc()})
    assert 'island "isl-budget" --causal--> island "isl-effect"' in _CAPTURED[0].prompt


def test_document_without_relations_says_none() -> None:
    doc = _doc()
    doc["edges"] = []
    doc["evidenceLinks"] = []
    with TestClient(app) as client:
        resp = client.post("/ai/generate-narrative", json={"doc": doc})
    assert resp.status_code == 200, resp.text
    prompt = _CAPTURED[0].prompt
    assert "Logical relations:\n- (none)" in prompt
    assert "Causal and oppositional structure" not in prompt


# ---------------------------------------------------------------------------
# Backward compatibility (AC-11) -- this endpoint HAS a frontend caller
# ---------------------------------------------------------------------------


def test_request_and_response_contract_are_unchanged() -> None:
    with TestClient(app) as client:
        resp = client.post(
            "/ai/generate-narrative",
            json={"doc": _doc(), "narrativeTitle": "補正予算の見立て"},
        )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert set(body) == {"text", "basedOnReadingOrder", "warnings"}
    assert body["basedOnReadingOrder"] == ["isl-budget", "isl-effect"]
    assert f"Narrative title hint: {json.dumps('補正予算の見立て')}" in _CAPTURED[0].prompt


def test_reading_order_lines_keep_the_mock_adapter_format() -> None:
    """`deploy/tools/mock_local_llm.py` parses the prompt with
    `^- \\d+\\. \\w+ id="([^"]+)"`; the business-flow E2E depends on it."""
    with TestClient(app) as client:
        client.post("/ai/generate-narrative", json={"doc": _doc()})
    prompt = _CAPTURED[0].prompt
    assert '- 1. island id="isl-budget", title=' in prompt
    assert '- 2. island id="isl-effect", title=' in prompt

    import re

    reading_order_line = re.compile(r'^- \d+\. \w+ id="([^"]+)"', re.MULTILINE)
    assert reading_order_line.findall(prompt) == ["isl-budget", "isl-effect"]


def test_reading_order_card_lines_keep_the_mock_adapter_format() -> None:
    doc = _doc()
    doc["readingOrder"] = ["c-budget", "c-cut"]
    _RESPONSE["basedOnReadingOrder"] = ["c-budget", "c-cut"]
    with TestClient(app) as client:
        client.post("/ai/generate-narrative", json={"doc": doc})
    prompt = _CAPTURED[0].prompt
    assert f'- 1. card id="c-budget", text={json.dumps(_TEXTS["c-budget"])}' in prompt

    import re

    reading_order_line = re.compile(r'^- \d+\. \w+ id="([^"]+)"', re.MULTILINE)
    assert reading_order_line.findall(prompt) == ["c-budget", "c-cut"]


def test_truncation_is_stated_in_the_prompt_rather_than_silent() -> None:
    """The IR caps the projection (spec §5.1). Sizing that cap is AC-10 and is
    deferred; the prompt must at least not present a truncated relation set as
    if it were the whole document."""
    from kj_atlas_api.llm_input_ir import MAX_CARDS

    doc = _doc()
    doc["cards"] = [
        {
            "id": f"k-{index:03d}",
            "text": f"観察その{index}を記録している",
            "x": index,
            "y": 0,
            "textReviewed": True,
        }
        for index in range(MAX_CARDS + 1)
    ]
    doc["edges"] = []
    doc["islands"] = [{"id": "isl-all", "cardIds": [], "title": "全体"}]
    doc["evidenceLinks"] = []
    doc["readingOrder"] = ["isl-all"]
    _RESPONSE["basedOnReadingOrder"] = ["isl-all"]

    with TestClient(app) as client:
        resp = client.post("/ai/generate-narrative", json={"doc": doc})
    assert resp.status_code == 200, resp.text
    assert "the projection hit its size limit" in _CAPTURED[0].prompt


def test_document_with_no_cards_is_refused_by_the_ir() -> None:
    """Behaviour change recorded on purpose: a document with nothing to narrate
    is now a 422 from the IR (spec §2.1 requires at least one card) instead of a
    narrative drafted from an empty prompt."""
    doc = _doc()
    doc["cards"] = []
    doc["edges"] = []
    doc["islands"] = []
    doc["evidenceLinks"] = []
    doc["readingOrder"] = []
    with TestClient(app) as client:
        resp = client.post("/ai/generate-narrative", json={"doc": doc})
    assert resp.status_code == 422
    assert resp.json()["detail"]["code"] == "empty_cards"
    assert _CAPTURED == []


# ---------------------------------------------------------------------------
# SafeMode: layer 1 unchanged, layer 2 added
# ---------------------------------------------------------------------------


def test_existing_reject_unreviewed_text_behaviour_is_unchanged() -> None:
    """Regression proof for SEC-AI-SAFEMODE-01: the shipped 422 still fires,
    with the same code, and still fires BEFORE any LLM call."""
    doc = _doc()
    doc["cards"][1].pop("textReviewed")
    with TestClient(app) as client:
        resp = client.post("/ai/generate-narrative", json={"doc": doc})
    assert resp.status_code == 422
    detail = resp.json()["detail"]
    assert detail["code"] == "unreviewed_text_not_allowed"
    assert "cannot be sent to the LLM under SafeMode" in detail["message"]
    assert _CAPTURED == []


def test_ir_layer_refuses_unreviewed_text_independently_of_the_route_gate() -> None:
    """Layer 2 is independent, not a rename of layer 1.

    On this endpoint both layers read the same `doc`, so the route gate always
    fires first -- there is no request that reaches the IR with unreviewed text.
    The builder is therefore driven directly to show that it would refuse on its
    own if a future caller ever skipped the route gate
    (llm_input_ir_spec.md §7.1, ADR-0069 defense-in-depth).
    """
    from kj_atlas_api.models_ai import GenerateNarrativeRequest

    raw = _doc()
    raw["cards"][0].pop("textReviewed")
    payload = GenerateNarrativeRequest.model_validate({"doc": raw})

    with pytest.raises(Exception) as excinfo:
        ai._generate_narrative_ir(payload)
    assert excinfo.value.status_code == 422
    assert excinfo.value.detail["code"] == "unreviewed_text_not_allowed"


def test_ir_layer_rejects_pii_in_document_text() -> None:
    doc = _doc()
    doc["cards"][0]["text"] = "連絡先は contact@example.com である"
    with TestClient(app) as client:
        resp = client.post("/ai/generate-narrative", json={"doc": doc})
    assert resp.status_code == 422
    detail = resp.json()["detail"]
    assert detail["code"] == "pii_detected"
    # SEC-VALIDATION-LEAK-01: the rejected value is not reflected back.
    assert "contact@example.com" not in json.dumps(detail, ensure_ascii=False)
    assert _CAPTURED == []


def test_allow_unreviewed_text_still_relaxes_both_layers_together() -> None:
    """The relaxation switch must not become half-open: when the profile permits
    it, the IR layer agrees with the route gate instead of contradicting it."""
    doc = _doc()
    doc["cards"][1].pop("textReviewed")
    settings.allow_unreviewed_ai_text = True
    try:
        with TestClient(app) as client:
            resp = client.post(
                "/ai/generate-narrative",
                json={"doc": doc, "allowUnreviewedText": True},
            )
    finally:
        settings.allow_unreviewed_ai_text = False
    assert resp.status_code == 200, resp.text
    assert _CAPTURED[0].inputs["ir_version"] == IR_VERSION
