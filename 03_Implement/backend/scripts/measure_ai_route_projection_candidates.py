#!/usr/bin/env python3
"""Compare current shared-IR prompts with route-specific B candidates.

This is an AI-IR-SCALE-01 characterization only.  It does not change
production routing, shared IR caps, or provider selection, and it never
calls an LLM.  The candidate contexts deliberately retain only the
route-required meaning identified in R19 so we can see whether a
task-specific projection can restore 300-card coverage before choosing
A2/B/C from provider-reported token measurements.
"""

from __future__ import annotations

import json
from copy import deepcopy
from typing import Any

from kj_atlas_api.llm_input_ir import (
    _normalize_cards,
    _normalize_coordinates,
    _normalize_islands,
    _normalize_relations,
    source_from_document,
)
from kj_atlas_api.models import SuggestLayoutRequest
from kj_atlas_api.models_ai import SuggestCardGroupsRequest
from kj_atlas_api.routes.ai import (
    _build_prompt,
    _build_suggest_card_groups_prompt,
    _card_group_candidates,
    _suggest_card_groups_ir,
    _suggest_layout_ir,
)
try:
    from scripts.measure_ai_route_prompt_coverage import representative_document
except ModuleNotFoundError as exc:
    if exc.name != "scripts":
        raise
    from measure_ai_route_prompt_coverage import representative_document

TAIL_A = "c298"
TAIL_B = "c299"
TAIL_ISLAND = "i29"


def _prompt_size(prompt: str) -> dict[str, int]:
    return {
        "unicode_chars": len(prompt),
        "utf8_bytes": len(prompt.encode("utf-8")),
    }


def _complete_island_memberships(doc: dict[str, Any], context: dict[str, Any]) -> int:
    source = {item["id"]: sorted(item["cardIds"]) for item in doc["islands"]}
    projected = {
        item["id"]: sorted(item["card_ids"])
        for item in context.get("islands", [])
    }
    return sum(projected.get(island_id) == members for island_id, members in source.items())


def _groups_candidate_context(payload: SuggestCardGroupsRequest) -> dict[str, Any]:
    """Measurement-only compact context for R19's grouping-required meaning.

    Candidate text/hold state and confirmed island hierarchy are kept.
    Relations and derived clusters are intentionally omitted because R19
    classifies them as useful supplemental context, not completion criteria.
    The shape is only accepted by the existing deterministic renderer for
    measurement; it is not a new serialized IR contract.
    """
    assert payload.doc is not None
    source = source_from_document(payload.doc)
    requested_ids = {card.id for card in payload.cards}
    normalized_cards = _normalize_cards(source.cards)
    rows: list[dict[str, Any]] = []
    for card in normalized_cards:
        if card.id not in requested_ids:
            continue
        row: dict[str, Any] = {"id": card.id, "text": card.text}
        if card.hold_state is not None:
            row["hold_state"] = card.hold_state
        rows.append(row)
    islands = _normalize_islands(source.islands, requested_ids)
    return {
        "cards": rows,
        "islands": islands,
        "relations": [],
        "truncation": {"truncated": False, "reason_codes": []},
    }


def _layout_candidate_context(payload: SuggestLayoutRequest) -> dict[str, Any]:
    """Measurement-only full structural context for layout.

    The existing layout prompt already carries every card id/text/raw x/y
    from DocumentV1.  The candidate therefore adds only the route-required
    structural dimensions that the shared 200-card IR currently truncates:
    normalized relative coordinates, typed card relations and confirmed
    island hierarchy.  No production contract is changed here.
    """
    source = source_from_document(payload.doc)
    normalized_cards = _normalize_cards(source.cards)
    card_ids = {card.id for card in normalized_cards}
    return {
        "coordinates": _normalize_coordinates(normalized_cards),
        "relations": _normalize_relations(source.relations, card_ids),
        "islands": _normalize_islands(source.islands, card_ids),
        "truncation": {"truncated": False, "reason_codes": []},
    }


def _grouping_measurement() -> dict[str, Any]:
    doc = representative_document(include_evidence=False)
    next(item for item in doc["cards"] if item["id"] == TAIL_A)["holdState"] = "held"
    payload = SuggestCardGroupsRequest.model_validate(
        {
            "doc": doc,
            "cards": [
                {
                    "id": card["id"],
                    "text": card["text"],
                    "textReviewed": True,
                }
                for card in doc["cards"]
            ],
        }
    )

    current_ir = _suggest_card_groups_ir(payload)
    current_candidates, current_withheld = _card_group_candidates(payload, current_ir)
    current_prompt = _build_suggest_card_groups_prompt(
        payload, current_ir, current_candidates
    )

    candidate_context = _groups_candidate_context(payload)
    candidate_ids, candidate_withheld = _card_group_candidates(
        payload, candidate_context
    )
    candidate_prompt = _build_suggest_card_groups_prompt(
        payload, candidate_context, candidate_ids
    )

    requested_count = len(payload.cards)
    return {
        "source": {
            "requested_cards": requested_count,
            "held_requested_cards": 1,
            "islands": len(doc["islands"]),
        },
        "current_shared_ir": {
            "projected_requested_cards": sum(
                item["id"] in {card.id for card in payload.cards}
                for item in current_ir["cards"]
            ),
            "groupable_candidates": len(current_candidates),
            "withheld_held_cards": len(current_withheld),
            "requested_cards_accounted_for": len(current_candidates)
            + len(current_withheld),
            "complete_island_memberships": _complete_island_memberships(doc, current_ir),
            "tail_island_members": len(
                next(
                    item
                    for item in current_ir["islands"]
                    if item["id"] == TAIL_ISLAND
                )["card_ids"]
            ),
            "prompt": _prompt_size(current_prompt),
        },
        "route_b_candidate": {
            "projected_requested_cards": len(candidate_context["cards"]),
            "groupable_candidates": len(candidate_ids),
            "withheld_held_cards": len(candidate_withheld),
            "requested_cards_accounted_for": len(candidate_ids)
            + len(candidate_withheld),
            "complete_island_memberships": _complete_island_memberships(
                doc, candidate_context
            ),
            "tail_island_members": len(
                next(
                    item
                    for item in candidate_context["islands"]
                    if item["id"] == TAIL_ISLAND
                )["card_ids"]
            ),
            "prompt": _prompt_size(candidate_prompt),
        },
    }


def _late_layout_document() -> dict[str, Any]:
    doc = deepcopy(representative_document(include_evidence=False))
    for edge in doc["edges"]:
        if edge["id"] == "e298":
            edge["type"] = "causal"
        elif edge["id"] == "e299":
            edge["type"] = "negate"
    return doc


def _layout_measurement() -> dict[str, Any]:
    doc = _late_layout_document()
    payload = SuggestLayoutRequest.model_validate({"doc": doc})
    current_ir = _suggest_layout_ir(payload)
    current_prompt = _build_prompt(payload, current_ir)
    candidate_context = _layout_candidate_context(payload)
    candidate_prompt = _build_prompt(payload, candidate_context)

    expected = {
        (TAIL_A, TAIL_B, "causal"),
        (TAIL_B, "c000", "negate"),
    }

    def metrics(context: dict[str, Any], prompt: str) -> dict[str, Any]:
        coordinate_ids = {
            item["card_id"] for item in context.get("coordinates", [])
        }
        relations = {
            (item["from"], item["to"], item["type"])
            for item in context.get("relations", [])
        }
        return {
            "relative_coordinates": len(coordinate_ids),
            "typed_card_relations": len(relations),
            "complete_island_memberships": _complete_island_memberships(
                doc, context
            ),
            "tail_coordinates_present": [
                card_id
                for card_id in (TAIL_A, TAIL_B)
                if card_id in coordinate_ids
            ],
            "tail_required_relations_present": sorted(expected & relations),
            "tail_causal_visible_in_prompt": (
                f'card "{TAIL_A}" --causal--> card "{TAIL_B}"' in prompt
            ),
            "tail_negate_visible_in_prompt": (
                'card "c299" --negate--> card "c000"' in prompt
            ),
            "prompt": _prompt_size(prompt),
        }

    return {
        "source": {
            "cards": len(doc["cards"]),
            "typed_card_relations": len(doc["edges"]),
            "islands": len(doc["islands"]),
        },
        "current_shared_ir": metrics(current_ir, current_prompt),
        "route_b_candidate": metrics(candidate_context, candidate_prompt),
    }


def measure() -> dict[str, Any]:
    return {
        "measurement": "ai-route-specific-projection-candidates-at-scale",
        "groups": _grouping_measurement(),
        "layout": _layout_measurement(),
        "interpretation_boundary": (
            "Measurement-only route-B candidates. No provider is called; prompt bytes are "
            "not token counts; no production projection contract or cap is changed."
        ),
    }


def main() -> int:
    print(json.dumps(measure(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
