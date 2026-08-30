"""Integration tests for `/ai/suggest-layout` on the LLM input IR path.

Stage 4 of the `ADR-0069` rollout (`AI-IR-PROJECTION-01`). This endpoint differs
from stages 1-3 in the one way the ADR singled out: it is the ONLY endpoint that
declares `coordinates` required (spec §2.2.1, D1=B), because here the output IS
placement. Four things are being proven:

1. Coordinates reach the model NORMALIZED per spec §2.2 -- centroid translated
   to the origin, with `radius` and `angle_deg` -- and not as the raw absolute
   values. The raw values keep their own separate section because the response
   is in the document's absolute space, but the IR never carries them.
2. The relations reach the model ("あわせて `edges` を渡す", ADR-0069 実装順序 4),
   with `causal` and `negate` present as themselves.
3. Islands reach the model as RELATION SETS, not only as rectangles: the
   confirmed hierarchy (`parent_island_id` / `placard_card_id` / review state)
   plus the island-to-island relations aggregated from the card relations by
   `derived_island_relations()`. The pre-IR prompt described an island solely by
   a bounding box computed from raw card coordinates, which is the specific
   critique ADR-0069 raised against this endpoint.
4. The shipped request/response contract is untouched (AC-11) -- this endpoint
   HAS a frontend caller (`frontend/src/api/client.ts` `suggestLayout`, used from
   `App.tsx`) -- and the card-line format `deploy/tools/mock_local_llm.py` parses
   for `re_layout` is byte-compatible.

The pre-existing SafeMode gate (`_reject_unreviewed_text`, SEC-AI-SAFEMODE-01 /
ADR-0068) is unchanged; the IR's own check (spec §7.1) is an additional layer.
"""
from __future__ import annotations

import json
import re

import pytest
from fastapi.testclient import TestClient

from kj_atlas_api.llm_input_ir import IR_VERSION
from kj_atlas_api.main import app
from kj_atlas_api.routes import ai
from kj_atlas_api.settings import settings

_CAPTURED: list = []

#: Verbatim from `deploy/tools/mock_local_llm.py`. The stub answers the prompt
#: the way the mock adapter does, so every test in this module also exercises
#: that parser against the real prompt (AC-11).
_MOCK_CARD_LINE = re.compile(r'^\s*- id="([^"]+)", text=', re.MULTILINE)
_MOCK_GRID_COLUMNS = 4
_MOCK_GRID_SPACING_X = 280
_MOCK_GRID_SPACING_Y = 160


def _stub_generate(req):
    _CAPTURED.append(req)
    card_ids = _MOCK_CARD_LINE.findall(req.prompt)
    body = {
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
        "cards": [
            {
                "id": card_id,
                "x": (index % _MOCK_GRID_COLUMNS) * _MOCK_GRID_SPACING_X,
                "y": (index // _MOCK_GRID_COLUMNS) * _MOCK_GRID_SPACING_Y,
            }
            for index, card_id in enumerate(card_ids)
        ],
    }
    return type("R", (), {"raw_text": json.dumps(body)})()


@pytest.fixture(autouse=True)
def _stub_llm(monkeypatch: pytest.MonkeyPatch):
    _CAPTURED.clear()
    monkeypatch.setattr(ai, "generate_with_fallback", _stub_generate)
    monkeypatch.setattr(settings, "allow_unreviewed_ai_text", False)
    yield
    _CAPTURED.clear()


_TEXTS = {
    "c1": "補正予算の組み替えを説明している",
    "c2": "現場の人員配置がさらに絞られると見ている",
    "c3": "財源の裏づけが示されていないと見ている",
    "c4": "人員を絞っても現場は回ると考えている",
    "c5": "住民説明会の開催時期が決まっていない",
}

#: Positions chosen so the §2.2 normalization has exact expected values: the
#: centroid lands on (100, 100), so every normalized coordinate is a round number
#: and the assertions can name them instead of approximating.
_POSITIONS = {
    "c1": (0.0, 0.0),
    "c2": (100.0, 0.0),
    "c3": (0.0, 100.0),
    "c4": (100.0, 100.0),
    "c5": (300.0, 300.0),
}


def _card(card_id: str) -> dict:
    x, y = _POSITIONS[card_id]
    return {
        "id": card_id,
        "text": _TEXTS[card_id],
        "x": x,
        "y": y,
        "textReviewed": True,
    }


def _doc() -> dict:
    """Two islands pulled together by a `causal` edge and pushed apart by a
    `negate` one, plus a lone-wolf card (`c5`) related to a card inside an
    island. Those are the three island-relation shapes the layout has to weigh.
    """
    return {
        "version": 1,
        "id": "layout-ir-doc",
        "createdAt": "2026-08-31T00:00:00Z",
        "updatedAt": "2026-08-31T00:00:00Z",
        "transform": {"panX": 12, "panY": 34, "zoom": 1.25},
        "cards": [_card(card_id) for card_id in ("c1", "c2", "c3", "c4", "c5")],
        "edges": [
            {"id": "e-causal", "fromId": "c1", "toId": "c2", "type": "causal"},
            {"id": "e-negate", "fromId": "c3", "toId": "c4", "type": "negate"},
            # internal to isl-left: real structure, but not an island relation
            {"id": "e-internal", "fromId": "c1", "toId": "c3", "type": "related"},
            # island <-> lone wolf
            {"id": "e-lone", "fromId": "c1", "toId": "c5", "type": "related"},
            # spec §2.3 rule 6: excluded from the IR, not rejected
            {"id": "e-unknown", "fromId": "c2", "toId": "c4", "type": "unknown"},
            {
                "id": "e-island",
                "fromId": "isl-left",
                "toId": "isl-right",
                "fromKind": "island",
                "toKind": "island",
                "type": "related",
            },
        ],
        "islands": [
            {
                "id": "isl-left",
                "cardIds": ["c1", "c3"],
                "title": "予算の説明",
                "titleReviewed": True,
                "placardCardId": "c1",
            },
            {
                "id": "isl-right",
                "cardIds": ["c2", "c4"],
                "title": "現場への波及",
                "parentIslandId": "isl-left",
            },
        ],
    }


def _post(doc: dict | None = None, **extra) -> tuple[int, dict]:
    with TestClient(app) as client:
        resp = client.post("/ai/suggest-layout", json={"doc": doc or _doc(), **extra})
    return resp.status_code, (resp.json() if resp.content else {})


# ---------------------------------------------------------------------------
# Coordinates: the one endpoint that asks for them (spec §2.2.1 / ADR-0069 D1=B)
# ---------------------------------------------------------------------------


def test_ir_carries_coordinates_normalized_per_spec_2_2() -> None:
    """Centroid translated to the origin, plus radius / angle_deg.

    The document's centroid is (100, 100) by construction, so these are exact
    values rather than tolerances -- a builder that forgot the translation, or
    emitted polar values from the untranslated frame, fails here.
    """
    status, _ = _post()
    assert status == 200

    ir = _CAPTURED[0].inputs
    assert ir is not None
    assert ir["ir_version"] == IR_VERSION

    by_card = {item["card_id"]: item for item in ir["coordinates"]}
    assert set(by_card) == {"c1", "c2", "c3", "c4", "c5"}
    assert (by_card["c1"]["x"], by_card["c1"]["y"]) == (-100.0, -100.0)
    assert (by_card["c2"]["x"], by_card["c2"]["y"]) == (0.0, -100.0)
    assert (by_card["c3"]["x"], by_card["c3"]["y"]) == (-100.0, 0.0)
    assert (by_card["c4"]["x"], by_card["c4"]["y"]) == (0.0, 0.0)
    assert (by_card["c5"]["x"], by_card["c5"]["y"]) == (200.0, 200.0)

    assert by_card["c1"]["radius"] == 141.421
    assert by_card["c1"]["angle_deg"] == -135.0
    assert by_card["c2"]["radius"] == 100.0
    assert by_card["c2"]["angle_deg"] == -90.0
    assert by_card["c3"]["angle_deg"] == 180.0
    assert by_card["c5"]["radius"] == 282.843
    assert by_card["c5"]["angle_deg"] == 45.0


def test_ir_never_carries_the_raw_absolute_coordinates() -> None:
    """spec §2.2 rule 6: raw absolute coordinates must not enter the IR.

    The card entries themselves have no coordinate fields at all, and the
    normalized block is centred on the origin -- the document's own frame
    (0..300) does not survive into it.
    """
    _post()
    ir = _CAPTURED[0].inputs

    for card in ir["cards"]:
        assert "x" not in card and "y" not in card
    assert {item["x"] for item in ir["coordinates"]} == {-100.0, 0.0, 200.0}


def test_prompt_states_the_normalized_placement_and_marks_it_not_for_output() -> None:
    """The prompt is what the transport actually sends, so the normalization has
    to be visible there and not only on `LLMRequest.inputs`."""
    _post()
    prompt = _CAPTURED[0].prompt

    assert "Relative placement (centroid moved to the origin" in prompt
    assert "do NOT return these values" in prompt
    assert '- card "c1" at (x=-100.0, y=-100.0), radius=141.421, angle_deg=-135.0' in prompt
    assert '- card "c5" at (x=200.0, y=200.0), radius=282.843, angle_deg=45.0' in prompt


def test_spatial_cluster_candidates_exist_only_because_coordinates_were_requested() -> None:
    """A consequence of D1=B worth pinning: with coordinates present the IR also
    produces `basis="spatial"` candidates (spec §3.1 rule 2), which the other
    three migrated endpoints never see.

    They are carried on `LLMRequest.inputs` but deliberately NOT rendered into
    the prompt -- they are machine PROPOSALS, and the prompt already shows the
    human-confirmed `islands`. Putting both in front of the model invites it to
    re-group cards while it is being asked to place them, which is the CVI-2 /
    CVI-3 boundary (a candidate is not a decided island).
    """
    _post()
    ir = _CAPTURED[0].inputs

    bases = {cluster["basis"] for cluster in ir.get("cluster_candidates", [])}
    assert "spatial" in bases

    prompt = _CAPTURED[0].prompt
    assert "cluster_candidates" not in prompt
    assert "spatial" not in prompt


def test_absolute_coordinates_stay_in_the_cards_section() -> None:
    """Regression: the endpoint answers in the document's absolute space, and
    `_parse_suggestion()` requires a position for every document card. Replacing
    the raw values with the normalized ones would change the output frame."""
    _post()
    prompt = _CAPTURED[0].prompt

    assert f'- id="c1", text={json.dumps(_TEXTS["c1"])}, x=0.0, y=0.0' in prompt
    assert f'- id="c5", text={json.dumps(_TEXTS["c5"])}, x=300.0, y=300.0' in prompt


# ---------------------------------------------------------------------------
# Relations reach the model (ADR-0069 実装順序 4: "あわせて edges を渡す")
# ---------------------------------------------------------------------------


def test_ir_carries_the_typed_relations() -> None:
    _post()
    ir = _CAPTURED[0].inputs

    by_type = {relation["type"]: relation for relation in ir["relations"]}
    assert (by_type["causal"]["from"], by_type["causal"]["to"]) == ("c1", "c2")
    assert (by_type["negate"]["from"], by_type["negate"]["to"]) == ("c3", "c4")
    # spec §2.3 rule 6: `unknown` and island-endpoint edges are excluded.
    assert "unknown" not in by_type
    assert all(
        relation["from"] not in {"isl-left", "isl-right"} for relation in ir["relations"]
    )


def test_prompt_names_causal_and_negate_as_themselves() -> None:
    _post()
    prompt = _CAPTURED[0].prompt

    assert "Logical relations (these, not the current positions" in prompt
    assert 'card "c1" --causal--> card "c2"' in prompt
    assert 'card "c3" --negate--> card "c4"' in prompt
    assert 'card "c1" --related--> card "c5"' in prompt
    assert "keep the two sides of a 'negate' relation visibly apart" in prompt


def test_persisted_island_edges_are_still_listed() -> None:
    """They are excluded from the IR (spec §2.3 rule 6) and read off the
    document, the same way `getDerivedIslandEdges()` leaves an already-explicit
    island edge alone."""
    _post()
    assert (
        'island "isl-left" --related--> island "isl-right" (stated)' in _CAPTURED[0].prompt
    )


def test_a_document_without_relations_says_none() -> None:
    doc = _doc()
    doc["edges"] = []
    status, _ = _post(doc)
    assert status == 200
    prompt = _CAPTURED[0].prompt
    assert "Logical relations (these, not the current positions" in prompt
    assert "Island relations (aggregated from the card relations above):\n- (none)" in prompt


# ---------------------------------------------------------------------------
# Islands as relation sets, not only rectangles (ADR-0069 D3=A)
# ---------------------------------------------------------------------------


def test_islands_reach_the_model_as_confirmed_structure() -> None:
    """`parent_island_id` / `placard_card_id` / review state -- none of which the
    pre-IR prompt could express, because it only computed a bounding box."""
    _post()
    ir = _CAPTURED[0].inputs

    by_id = {island["id"]: island for island in ir["islands"]}
    assert by_id["isl-left"]["card_ids"] == ["c1", "c3"]
    assert by_id["isl-left"]["placard_card_id"] == "c1"
    assert by_id["isl-left"]["review_state"] == "human_reviewed"
    assert by_id["isl-right"]["parent_island_id"] == "isl-left"
    assert by_id["isl-right"]["review_state"] == "unreviewed"

    prompt = _CAPTURED[0].prompt
    assert 'parentIslandId=null, placardCardId="c1", reviewState="human_reviewed"' in prompt
    assert 'parentIslandId="isl-left", placardCardId=null, reviewState="unreviewed"' in prompt


def test_island_to_island_relations_are_derived_from_the_card_relations() -> None:
    """The AC-7 function pair, used for real: two islands that no persisted edge
    connects by `causal` are nonetheless shown as causally linked, because two of
    their member cards are."""
    _post()
    prompt = _CAPTURED[0].prompt

    assert "Island relations (aggregated from the card relations above):" in prompt
    assert (
        '- island "isl-left" --causal--> island "isl-right" '
        "(aggregated from 1 card relation(s): c1, c2)" in prompt
    )
    assert (
        '- island "isl-left" --negate--> island "isl-right" '
        "(aggregated from 1 card relation(s): c3, c4)" in prompt
    )
    assert (
        '- island "isl-left" --related--> lone card "c5" '
        "(aggregated from 1 card relation(s): c1, c5)" in prompt
    )


def test_a_relation_internal_to_one_island_is_not_escalated() -> None:
    """`c1 --related--> c3` sits inside `isl-left`; it says nothing about where
    the islands should go relative to each other."""
    _post()
    prompt = _CAPTURED[0].prompt

    assert 'card "c1" --related--> card "c3"' in prompt  # still listed as context
    assert '- island "isl-left" --related--> island "isl-left"' not in prompt


def test_bounding_boxes_are_kept_alongside_the_relations() -> None:
    """The critique was "islands are presented as rectangles", not "geometry is
    useless" -- this endpoint proposes NEW positions and needs the current frame.
    The fix is additive: bounds/anchor stay, relations arrive next to them."""
    _post()
    prompt = _CAPTURED[0].prompt

    assert "bounds=(0.00,0.00)-(0.00,100.00), anchor=(0.00,50.00)" in prompt
    assert "bounds=(100.00,0.00)-(100.00,100.00), anchor=(100.00,50.00)" in prompt


# ---------------------------------------------------------------------------
# Backward compatibility (AC-11) -- this endpoint HAS a frontend caller
# ---------------------------------------------------------------------------


def test_request_and_response_contract_are_unchanged() -> None:
    status, body = _post(instruction="島ごとに離して配置してほしい")
    assert status == 200
    assert set(body) == {"suggestionId", "suggestedDoc", "notes"}
    assert [card["id"] for card in body["suggestedDoc"]["cards"]] == [
        "c1",
        "c2",
        "c3",
        "c4",
        "c5",
    ]
    assert body["suggestedDoc"]["transform"] == {"panX": 0.0, "panY": 0.0, "zoom": 1.0}
    assert "Instruction: 島ごとに離して配置してほしい" in _CAPTURED[0].prompt


def test_card_lines_keep_the_mock_adapter_format() -> None:
    """`mock_local_llm.py` finds the cards for `re_layout` with
    `^\\s*- id="([^"]+)", text=`. Every new prompt line must stay outside that
    pattern, or the mock would invent cards and `_parse_suggestion()` would 422.
    """
    _post()
    prompt = _CAPTURED[0].prompt

    assert _MOCK_CARD_LINE.findall(prompt) == ["c1", "c2", "c3", "c4", "c5"]
    # The island lines are excluded by using `, title=` -- unchanged, but the new
    # sections must not reintroduce the collision either.
    island_line = re.compile(r'^- id="([^"]+)", title=', re.MULTILINE)
    assert island_line.findall(prompt) == ["isl-left", "isl-right"]


def test_transform_line_is_unchanged() -> None:
    _post()
    assert "Current transform: panX=12.0, panY=34.0, zoom=1.25" in _CAPTURED[0].prompt


def test_truncation_is_stated_in_the_prompt_rather_than_silent() -> None:
    """The IR caps the projection (spec §5.1) while the request may carry more
    cards. Sizing that cap is AC-10 and is deferred; the prompt must at least not
    present a partial relation set as if it covered every card."""
    from kj_atlas_api.llm_input_ir import MAX_CARDS

    doc = _doc()
    doc["cards"] = [
        {
            "id": f"k-{index:03d}",
            "text": f"観察その{index}を記録している",
            "x": float(index),
            "y": 0.0,
            "textReviewed": True,
        }
        for index in range(MAX_CARDS + 1)
    ]
    doc["edges"] = []
    doc["islands"] = []

    status, body = _post(doc)
    assert status == 200
    assert "the projection hit its size limit" in _CAPTURED[0].prompt
    # ...and every document card still gets a position back (the Cards section is
    # document-derived precisely so this stays true).
    assert len(body["suggestedDoc"]["cards"]) == MAX_CARDS + 1


def test_document_with_no_cards_is_refused_by_the_ir() -> None:
    """Behaviour change recorded on purpose: a document with nothing to place is
    now a 422 from the IR (spec §2.1 requires at least one card) instead of a
    layout drafted from an empty card list."""
    doc = _doc()
    doc["cards"] = []
    doc["edges"] = []
    doc["islands"] = []

    status, body = _post(doc)
    assert status == 422
    assert body["detail"]["code"] == "empty_cards"
    assert _CAPTURED == []


# ---------------------------------------------------------------------------
# SafeMode: layer 1 unchanged, layer 2 added
# ---------------------------------------------------------------------------


def test_existing_reject_unreviewed_text_behaviour_is_unchanged() -> None:
    """Regression proof for SEC-AI-SAFEMODE-01: the shipped 422 still fires,
    with the same code, and still fires BEFORE any LLM call."""
    doc = _doc()
    doc["cards"][1].pop("textReviewed")

    status, body = _post(doc)
    assert status == 422
    assert body["detail"]["code"] == "unreviewed_text_not_allowed"
    assert "cannot be sent to the LLM under SafeMode" in body["detail"]["message"]
    assert _CAPTURED == []


def test_ir_layer_refuses_unreviewed_text_independently_of_the_route_gate() -> None:
    """Layer 2 is independent, not a rename of layer 1.

    Both layers read the same `doc` here, so the route gate always fires first --
    no request reaches the IR with unreviewed text. The builder is therefore
    driven directly, to show it would refuse on its own if a future caller ever
    skipped the route gate (spec §7.1, ADR-0069 defense-in-depth).
    """
    from kj_atlas_api.models import SuggestLayoutRequest

    raw = _doc()
    raw["cards"][0].pop("textReviewed")
    payload = SuggestLayoutRequest.model_validate({"doc": raw})

    with pytest.raises(Exception) as excinfo:
        ai._suggest_layout_ir(payload)
    assert excinfo.value.status_code == 422
    assert excinfo.value.detail["code"] == "unreviewed_text_not_allowed"


def test_ir_layer_rejects_pii_in_document_text() -> None:
    doc = _doc()
    doc["cards"][0]["text"] = "連絡先は contact@example.com である"

    status, body = _post(doc)
    assert status == 422
    assert body["detail"]["code"] == "pii_detected"
    # SEC-VALIDATION-LEAK-01: the rejected value is not reflected back.
    assert "contact@example.com" not in json.dumps(body, ensure_ascii=False)
    assert _CAPTURED == []


def test_allow_unreviewed_text_relaxes_both_layers_together() -> None:
    """The relaxation switch must not become half-open: when the profile permits
    it, the IR layer agrees with the route gate instead of contradicting it."""
    doc = _doc()
    doc["cards"][1].pop("textReviewed")
    settings.allow_unreviewed_ai_text = True
    try:
        status, _ = _post(doc, allowUnreviewedText=True)
    finally:
        settings.allow_unreviewed_ai_text = False

    assert status == 200
    assert _CAPTURED[0].inputs is not None


def test_relaxation_is_still_refused_when_the_profile_forbids_it() -> None:
    doc = _doc()
    doc["cards"][1].pop("textReviewed")

    status, body = _post(doc, allowUnreviewedText=True)
    assert status == 422
    assert body["detail"]["code"] == "unreviewed_text_not_allowed"
    assert _CAPTURED == []
