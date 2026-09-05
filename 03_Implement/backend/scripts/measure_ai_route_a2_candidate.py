#!/usr/bin/env python3
"""Characterize a representative-fit A2 shared-IR candidate without changing caps.

AI-IR-SCALE-01 R21 keeps A2 (coordinated card/text budget expansion) as a
candidate but deliberately forbids changing production limits before named
provider/model usage is known. R23 characterized route-specific B, while R25
and R27 made layout C concrete. This script gives A2 the same deterministic
measurement treatment.

For the fixed 300-card representative scenario only, it temporarily raises the
shared IR's card budget to the source card count and the text budget to exactly
the normalized source-text total. Those values are a *lower-bound fixture fit*,
not proposed production limits and not a safety margin. The original module
constants are restored even when projection fails.

No provider is called. Prompt bytes/chars are diagnostic only and are never
converted to token counts.
"""

from __future__ import annotations

import json
from contextlib import contextmanager
from typing import Any, Iterator

import kj_atlas_api.llm_input_ir as ir_module
from kj_atlas_api.llm_input_ir import _normalize_cards, source_from_document
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
    from scripts.measure_ai_route_projection_candidates import (
        TAIL_A,
        TAIL_B,
        _groups_candidate_context,
        _late_layout_document,
        _layout_candidate_context,
    )
    from scripts.measure_ai_route_prompt_coverage import representative_document
except ModuleNotFoundError as exc:
    if exc.name != "scripts":
        raise
    from measure_ai_route_projection_candidates import (
        TAIL_A,
        TAIL_B,
        _groups_candidate_context,
        _late_layout_document,
        _layout_candidate_context,
    )
    from measure_ai_route_prompt_coverage import representative_document


def _prompt_size(prompt: str) -> dict[str, int]:
    return {
        "unicode_chars": len(prompt),
        "utf8_bytes": len(prompt.encode("utf-8")),
    }


def representative_fit_budget(doc: Any) -> dict[str, int]:
    """Return the minimum shared card/text budgets needed by this fixture.

    This intentionally does not invent headroom. It only answers what the
    deterministic 300-card representative source needs to avoid those two
    current truncation reasons. Raw representative-document dicts are accepted
    too, so the measurement helper cannot silently interpret them as empty
    duck-typed objects.
    """
    if isinstance(doc, dict):
        doc = SuggestLayoutRequest.model_validate({"doc": doc}).doc
    source = source_from_document(doc)
    normalized = _normalize_cards(source.cards)
    return {
        "max_cards": len(normalized),
        "max_text_chars": sum(card.char_len for card in normalized),
        "max_relations": ir_module.MAX_RELATIONS,
    }


@contextmanager
def _temporary_representative_fit_budget(doc: Any) -> Iterator[dict[str, int]]:
    """Temporarily fit A2's two coordinated budgets, restoring globals always."""
    budget = representative_fit_budget(doc)
    old_cards = ir_module.MAX_CARDS
    old_text = ir_module.MAX_TEXT_CHARS
    try:
        ir_module.MAX_CARDS = max(old_cards, budget["max_cards"])
        ir_module.MAX_TEXT_CHARS = max(old_text, budget["max_text_chars"])
        yield budget
    finally:
        ir_module.MAX_CARDS = old_cards
        ir_module.MAX_TEXT_CHARS = old_text


def _complete_island_memberships(doc: dict[str, Any], context: dict[str, Any]) -> int:
    source = {item["id"]: sorted(item["cardIds"]) for item in doc["islands"]}
    projected = {
        item["id"]: sorted(item["card_ids"])
        for item in context.get("islands", [])
    }
    return sum(projected.get(island_id) == members for island_id, members in source.items())


def _grouping_measurement() -> dict[str, Any]:
    doc = representative_document(include_evidence=False)
    next(card for card in doc["cards"] if card["id"] == TAIL_A)["holdState"] = "held"
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

    production_caps_before = {
        "max_cards": ir_module.MAX_CARDS,
        "max_text_chars": ir_module.MAX_TEXT_CHARS,
        "max_relations": ir_module.MAX_RELATIONS,
    }
    with _temporary_representative_fit_budget(payload.doc) as budget:
        a2_ir = _suggest_card_groups_ir(payload)
    production_caps_after = {
        "max_cards": ir_module.MAX_CARDS,
        "max_text_chars": ir_module.MAX_TEXT_CHARS,
        "max_relations": ir_module.MAX_RELATIONS,
    }

    a2_candidates, a2_withheld = _card_group_candidates(payload, a2_ir)
    a2_prompt = _build_suggest_card_groups_prompt(payload, a2_ir, a2_candidates)

    b_context = _groups_candidate_context(payload)
    b_candidates, b_withheld = _card_group_candidates(payload, b_context)
    b_prompt = _build_suggest_card_groups_prompt(payload, b_context, b_candidates)

    return {
        "source": {
            "requested_cards": len(payload.cards),
            "held_requested_cards": 1,
            "islands": len(doc["islands"]),
        },
        "representative_fit_budget": budget,
        "production_caps_restored": production_caps_before == production_caps_after,
        "production_caps": production_caps_after,
        "a2_lower_bound_candidate": {
            "projected_cards": len(a2_ir.get("cards", [])),
            "relations": len(a2_ir.get("relations", [])),
            "complete_island_memberships": _complete_island_memberships(doc, a2_ir),
            "groupable_candidates": len(a2_candidates),
            "withheld_held_cards": len(a2_withheld),
            "truncation": a2_ir.get("truncation"),
            "prompt": _prompt_size(a2_prompt),
        },
        "route_b_candidate": {
            "projected_cards": len(b_context.get("cards", [])),
            "relations": len(b_context.get("relations", [])),
            "complete_island_memberships": _complete_island_memberships(doc, b_context),
            "groupable_candidates": len(b_candidates),
            "withheld_held_cards": len(b_withheld),
            "truncation": b_context.get("truncation"),
            "prompt": _prompt_size(b_prompt),
        },
        "rendered_prompt_equivalent_to_b": a2_prompt == b_prompt,
    }


def _layout_measurement() -> dict[str, Any]:
    doc = _late_layout_document()
    payload = SuggestLayoutRequest.model_validate({"doc": doc})

    production_caps_before = {
        "max_cards": ir_module.MAX_CARDS,
        "max_text_chars": ir_module.MAX_TEXT_CHARS,
        "max_relations": ir_module.MAX_RELATIONS,
    }
    with _temporary_representative_fit_budget(payload.doc) as budget:
        a2_ir = _suggest_layout_ir(payload)
    production_caps_after = {
        "max_cards": ir_module.MAX_CARDS,
        "max_text_chars": ir_module.MAX_TEXT_CHARS,
        "max_relations": ir_module.MAX_RELATIONS,
    }
    a2_prompt = _build_prompt(payload, a2_ir)

    b_context = _layout_candidate_context(payload)
    b_prompt = _build_prompt(payload, b_context)

    expected_tail_relations = {
        (TAIL_A, TAIL_B, "causal"),
        (TAIL_B, "c000", "negate"),
    }

    def metrics(context: dict[str, Any], prompt: str) -> dict[str, Any]:
        coordinates = {row["card_id"] for row in context.get("coordinates", [])}
        relations = {
            (row["from"], row["to"], row["type"])
            for row in context.get("relations", [])
        }
        return {
            "projected_cards": len(context.get("cards", [])),
            "relative_coordinates": len(coordinates),
            "relations": len(relations),
            "complete_island_memberships": _complete_island_memberships(doc, context),
            "tail_coordinates_present": sorted(
                card_id for card_id in (TAIL_A, TAIL_B) if card_id in coordinates
            ),
            "tail_required_relations_present": sorted(expected_tail_relations & relations),
            "truncation": context.get("truncation"),
            "prompt": _prompt_size(prompt),
        }

    return {
        "source": {
            "cards": len(doc["cards"]),
            "relations": len(doc["edges"]),
            "islands": len(doc["islands"]),
        },
        "representative_fit_budget": budget,
        "production_caps_restored": production_caps_before == production_caps_after,
        "production_caps": production_caps_after,
        "a2_lower_bound_candidate": metrics(a2_ir, a2_prompt),
        "route_b_candidate": metrics(b_context, b_prompt),
        "rendered_prompt_equivalent_to_b": a2_prompt == b_prompt,
    }


def measure() -> dict[str, Any]:
    return {
        "measurement": "ai-route-a2-lower-bound-candidate-at-scale",
        "groups": _grouping_measurement(),
        "layout": _layout_measurement(),
        "interpretation_boundary": (
            "The temporary 300-card / 13,800-text-character fit is a lower-bound fixture "
            "characterization, not a proposed production cap or safety margin. No provider is "
            "called; prompt bytes are not token counts; production constants are restored."
        ),
    }


def main() -> int:
    print(json.dumps(measure(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
