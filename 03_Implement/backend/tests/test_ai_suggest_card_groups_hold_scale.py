"""Scale regressions for human hold-state preservation in suggest-card-groups.

The grouping route must preserve a requested card's explicit human hold decision
before the global MAX_CARDS cut.  It must not, however, reserve unrelated held
cards that are not part of the current grouping request.
"""

from __future__ import annotations

from kj_atlas_api.models_ai import SuggestCardGroupsRequest
from kj_atlas_api.routes.ai import (
    _build_suggest_card_groups_prompt,
    _card_group_candidates,
    _suggest_card_groups_ir,
)
from scripts.measure_ai_route_prompt_coverage import representative_document


def _card_ref(doc: dict, card_id: str) -> dict:
    card = next(item for item in doc["cards"] if item["id"] == card_id)
    return {
        "id": card["id"],
        "text": card["text"],
        "textReviewed": True,
    }


def test_requested_tail_hold_survives_global_card_cut() -> None:
    doc = representative_document(include_evidence=False)
    tail = next(item for item in doc["cards"] if item["id"] == "c298")
    tail["holdState"] = "held"
    payload = SuggestCardGroupsRequest.model_validate(
        {
            "doc": doc,
            "cards": [_card_ref(doc, item["id"]) for item in doc["cards"]],
        }
    )

    ir = _suggest_card_groups_ir(payload)
    candidate_ids, withheld = _card_group_candidates(payload, ir)
    prompt = _build_suggest_card_groups_prompt(payload, ir, candidate_ids)

    by_id = {card["id"]: card for card in ir["cards"]}
    by_island = {island["id"]: island for island in ir["islands"]}
    assert len(ir["cards"]) == 200
    assert ir["truncation"] == {
        "truncated": True,
        "reason_codes": ["MAX_CARDS"],
    }
    assert by_id["c298"]["hold_state"] == "held"
    assert "c298" not in candidate_ids
    assert withheld == ["c298"]
    assert by_island["i29"]["card_ids"] == ["c298"]
    assert "c298 (holdState=held)" in prompt
    assert 'i29 "島29"' in prompt
    assert "members=c298" in prompt


def test_unrequested_tail_hold_does_not_consume_required_budget() -> None:
    doc = representative_document(include_evidence=False)
    requested_hold = next(item for item in doc["cards"] if item["id"] == "c298")
    unrelated_hold = next(item for item in doc["cards"] if item["id"] == "c299")
    requested_hold["holdState"] = "pending"
    unrelated_hold["holdState"] = "shelved"

    requested_ids = [item["id"] for item in doc["cards"] if item["id"] != "c299"]
    payload = SuggestCardGroupsRequest.model_validate(
        {
            "doc": doc,
            "cards": [_card_ref(doc, card_id) for card_id in requested_ids],
        }
    )

    ir = _suggest_card_groups_ir(payload)
    candidate_ids, withheld = _card_group_candidates(payload, ir)
    projected = {card["id"] for card in ir["cards"]}

    assert "c298" in projected
    assert "c298" not in candidate_ids
    assert withheld == ["c298"]
    # c299 has a document-level holdState but is outside this grouping request;
    # it therefore competes normally in the global projection and is not
    # reserved merely because another workflow may care about its hold state.
    assert "c299" not in projected
