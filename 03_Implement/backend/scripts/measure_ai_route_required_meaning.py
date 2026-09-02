#!/usr/bin/env python3
"""Characterize task-required semantic coverage at representative scale.

This probe complements ``measure_ai_route_prompt_coverage.py``.  The older
measurement deliberately counts broad source/IR/prompt dimensions.  R16 showed
that a difference is not automatically a defect: every AI route has a different
job and therefore a different required semantic set.

The scenarios below put route-required meaning near the tail of a deterministic
300-card / 30-island document, where the current global ``MAX_CARDS=200``
selection is most likely to remove it.  No provider is called.

This file is a characterization probe, not a remediation policy.  Its output
records what the current projector does so ``AI-IR-SCALE-01`` can choose a
meaning-preserving projection deliberately rather than simply raising caps.
"""

from __future__ import annotations

import json
from copy import deepcopy
from typing import Any

from kj_atlas_api.llm_input_ir import adjudicated_contradiction
from kj_atlas_api.models import SuggestLayoutRequest
from kj_atlas_api.models_ai import (
    DetectContradictionRequest,
    GenerateNarrativeRequest,
    SuggestCardGroupsRequest,
)
from kj_atlas_api.routes.ai import (
    _build_detect_contradiction_prompt,
    _build_generate_narrative_prompt,
    _build_prompt,
    _build_suggest_card_groups_prompt,
    _card_group_candidates,
    _detect_contradiction_ir,
    _generate_narrative_ir,
    _suggest_card_groups_ir,
    _suggest_layout_ir,
)
from scripts.measure_ai_route_prompt_coverage import representative_document

TAIL_A = "c298"
TAIL_B = "c299"
TAIL_ISLAND = "i29"


def _card_ref(doc: dict[str, Any], card_id: str) -> dict[str, Any]:
    card = next(item for item in doc["cards"] if item["id"] == card_id)
    return {
        "id": card["id"],
        "text": card["text"],
        "textReviewed": True,
    }


def _truncation(ir: dict[str, Any]) -> dict[str, Any]:
    return dict(ir.get("truncation") or {})


def measure_detect_target_tail() -> dict[str, Any]:
    """Put an already-held contradiction on the explicitly requested tail pair."""
    doc = representative_document(include_evidence=False)
    doc["evidenceLinks"] = [
        {
            "id": "ev-tail-held",
            "type": "contradicts",
            "fromCardId": TAIL_A,
            "toCardId": TAIL_B,
            "contradictionState": "held",
        }
    ]
    payload = DetectContradictionRequest.model_validate(
        {
            "cardA": _card_ref(doc, TAIL_A),
            "cardB": _card_ref(doc, TAIL_B),
            "doc": doc,
        }
    )
    ir = _detect_contradiction_ir(payload)
    prompt = _build_detect_contradiction_prompt(payload, ir)
    ir_card_ids = {item["id"] for item in ir.get("cards", [])}
    evidence_ids = {item["id"] for item in ir.get("evidence_links", [])}
    decided = adjudicated_contradiction(ir, TAIL_A, TAIL_B)

    return {
        "source": {
            "focus_cards": [TAIL_A, TAIL_B],
            "held_evidence": "ev-tail-held",
        },
        "ir": {
            "focus_cards_present": [card_id for card_id in (TAIL_A, TAIL_B) if card_id in ir_card_ids],
            "held_evidence_present": "ev-tail-held" in evidence_ids,
            "adjudicated_contradiction_found": decided is not None,
            "truncation": _truncation(ir),
        },
        # The route prompt still carries the two explicit request texts.  This
        # separates "the pair is visible" from "the human's prior judgement is
        # still visible", which is the AC-1 concern.
        "prompt": {
            "focus_card_a_visible": payload.cardA.text in prompt,
            "focus_card_b_visible": payload.cardB.text in prompt,
            "held_state_visible": "contradictionState=held" in prompt,
        },
    }


def measure_groups_late_island_and_hold() -> dict[str, Any]:
    """Place a human hold decision inside the last existing island."""
    doc = representative_document(include_evidence=False)
    tail = next(item for item in doc["cards"] if item["id"] == TAIL_A)
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
    islands = {item["id"]: item for item in ir.get("islands", [])}
    tail_island = islands.get(TAIL_ISLAND)
    held_in_ir = {
        item["id"] for item in ir.get("cards", []) if item.get("hold_state") == "held"
    }

    return {
        "source": {
            "tail_island_member_count": 10,
            "held_card": TAIL_A,
        },
        "ir": {
            "tail_island_present": tail_island is not None,
            "tail_island_member_count": len(tail_island["card_ids"]) if tail_island else None,
            "held_card_present": TAIL_A in held_in_ir,
            "truncation": _truncation(ir),
        },
        "grouping": {
            "held_card_withheld": TAIL_A in withheld,
            "held_card_candidate": TAIL_A in candidate_ids,
            "tail_island_membership_visible_in_prompt": (
                f'{TAIL_ISLAND} "島29"' in prompt and f"members={TAIL_A}" in prompt
            ),
        },
    }


def _late_structure_document() -> dict[str, Any]:
    doc = deepcopy(representative_document(include_evidence=False))
    # Replace the last two ring relations with route-significant relation types.
    for edge in doc["edges"]:
        if edge["id"] == "e298":
            edge["type"] = "causal"
        elif edge["id"] == "e299":
            edge["type"] = "negate"
    return doc


def measure_narrative_late_causal_negate() -> dict[str, Any]:
    """Put the AC-3 narrative skeleton on relations whose endpoints are late."""
    doc = _late_structure_document()
    payload = GenerateNarrativeRequest.model_validate({"doc": doc})
    ir = _generate_narrative_ir(payload)
    prompt = _build_generate_narrative_prompt(payload, ir)
    relations = {
        (item["from"], item["to"], item["type"]) for item in ir.get("relations", [])
    }
    expected = {
        (TAIL_A, TAIL_B, "causal"),
        (TAIL_B, "c000", "negate"),
    }

    return {
        "source": {
            "required_relations": sorted(expected),
            "reading_order_contains_tail_island": TAIL_ISLAND in doc["readingOrder"],
        },
        "ir": {
            "required_relations_present": sorted(expected & relations),
            "truncation": _truncation(ir),
        },
        "prompt": {
            "causal_visible": f'card "{TAIL_A}" --causal--> card "{TAIL_B}"' in prompt,
            "negate_visible": 'card "c299" --negate--> card "c000"' in prompt,
            "tail_island_visible": f'island id="{TAIL_ISLAND}"' in prompt,
        },
    }


def measure_layout_late_structure() -> dict[str, Any]:
    """Measure whether late-card placement and logical structure reach layout."""
    doc = _late_structure_document()
    payload = SuggestLayoutRequest.model_validate({"doc": doc})
    ir = _suggest_layout_ir(payload)
    prompt = _build_prompt(payload, ir)
    coordinate_ids = {item["card_id"] for item in ir.get("coordinates", [])}
    relations = {
        (item["from"], item["to"], item["type"]) for item in ir.get("relations", [])
    }
    expected = {
        (TAIL_A, TAIL_B, "causal"),
        (TAIL_B, "c000", "negate"),
    }

    return {
        "source": {
            "focus_cards": [TAIL_A, TAIL_B],
            "required_relations": sorted(expected),
        },
        "ir": {
            "focus_coordinates_present": [
                card_id for card_id in (TAIL_A, TAIL_B) if card_id in coordinate_ids
            ],
            "required_relations_present": sorted(expected & relations),
            "truncation": _truncation(ir),
        },
        "prompt": {
            "tail_card_a_visible_in_legacy_cards": payload.doc.cards[298].text in prompt,
            "tail_card_b_visible_in_legacy_cards": payload.doc.cards[299].text in prompt,
            "tail_relative_coordinate_a_visible": f'- card "{TAIL_A}" at (' in prompt,
            "tail_relative_coordinate_b_visible": f'- card "{TAIL_B}" at (' in prompt,
            "causal_visible": f'card "{TAIL_A}" --causal--> card "{TAIL_B}"' in prompt,
            "negate_visible": 'card "c299" --negate--> card "c000"' in prompt,
        },
    }


def measure() -> dict[str, Any]:
    return {
        "measurement": "ai-route-required-meaning-at-scale",
        "scenarios": {
            "detect-target-tail": measure_detect_target_tail(),
            "groups-late-islands-and-holds": measure_groups_late_island_and_hold(),
            "narrative-late-causal-negate": measure_narrative_late_causal_negate(),
            "layout-late-structure": measure_layout_late_structure(),
        },
        "interpretation_boundary": (
            "This characterizes deterministic projection and prompt visibility only. "
            "It does not decide the remediation policy or measure model quality."
        ),
    }


def main() -> int:
    print(json.dumps(measure(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
