#!/usr/bin/env python3
"""Measure final-prompt semantic coverage for the migrated AI routes.

AI-IR-SCALE-01 separates the shared LLM input IR from what a provider actually
receives.  The provider transport sends ``LLMRequest.prompt``; ``inputs`` is an
internal audit/diagnostic field.  A card can therefore disappear from the IR but
still survive in a route's legacy prompt section, or the reverse can happen for
relation/evidence structure.

This script calls the real deterministic projection/prompt helpers without
calling an LLM.  It measures two 300-card / 30-island scenarios:

- ``base``: the same 300-card ring used by ``measure_llm_input_ir_scale.py``;
- ``with_evidence``: the same source plus one held contradiction evidence link
  per island, so route-specific evidence rendering is observable.

The report deliberately keeps dimensions separate.  A single percentage would
hide the important case where every card text is present but relation or
membership structure is not.
"""

from __future__ import annotations

import json
from typing import Any

from kj_atlas_api.models import SuggestLayoutRequest
from kj_atlas_api.models_ai import GenerateNarrativeRequest, SuggestCardGroupsRequest
from kj_atlas_api.routes.ai import (
    _build_generate_narrative_prompt,
    _build_prompt,
    _build_suggest_card_groups_prompt,
    _card_group_candidates,
    _generate_narrative_ir,
    _suggest_card_groups_ir,
    _suggest_layout_ir,
)

CARD_COUNT = 300
ISLAND_COUNT = 30
CARDS_PER_ISLAND = 10


def representative_document(*, include_evidence: bool = False) -> dict[str, Any]:
    cards = [
        {
            "id": f"c{i:03d}",
            "text": (
                f"観察{i:03d}: 根拠・異論・保留を失わず、"
                "後から判断の経路へ戻れるように残した代表規模カード。"
            ),
            "x": float(i % 30),
            "y": float(i // 30),
            "textReviewed": True,
        }
        for i in range(CARD_COUNT)
    ]
    islands = [
        {
            "id": f"i{i:02d}",
            "cardIds": [
                f"c{card_index:03d}"
                for card_index in range(i * CARDS_PER_ISLAND, (i + 1) * CARDS_PER_ISLAND)
            ],
            "title": f"島{i:02d}",
            "titleReviewed": True,
        }
        for i in range(ISLAND_COUNT)
    ]
    edges = [
        {
            "id": f"e{i:03d}",
            "fromId": f"c{i:03d}",
            "toId": f"c{(i + 1) % CARD_COUNT:03d}",
            "type": "related",
        }
        for i in range(CARD_COUNT)
    ]
    evidence_links = []
    if include_evidence:
        evidence_links = [
            {
                "id": f"ev{i:02d}",
                "type": "contradicts",
                "fromCardId": f"c{i * CARDS_PER_ISLAND:03d}",
                "toCardId": f"c{i * CARDS_PER_ISLAND + 1:03d}",
                "contradictionState": "held",
            }
            for i in range(ISLAND_COUNT)
        ]

    return {
        "version": 1,
        "id": "representative-route-prompt-300x30",
        "createdAt": "2026-09-03T00:00:00Z",
        "updatedAt": "2026-09-03T00:00:00Z",
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
        "cards": cards,
        "edges": edges,
        "islands": islands,
        "evidenceLinks": evidence_links,
        "readingOrder": [f"i{i:02d}" for i in range(ISLAND_COUNT)],
    }


def _count(prompt: str, needles: list[str]) -> int:
    return sum(needle in prompt for needle in needles)


def _card_text_needles() -> list[str]:
    return [f"観察{i:03d}:" for i in range(CARD_COUNT)]


def _island_title_needles() -> list[str]:
    return [f"島{i:02d}" for i in range(ISLAND_COUNT)]


def _relation_needles(route: str) -> list[str]:
    if route == "suggest-card-groups":
        return [
            f"- related: c{i:03d} -> c{(i + 1) % CARD_COUNT:03d}"
            for i in range(CARD_COUNT)
        ]
    return [
        f'card "c{i:03d}" --related--> card "c{(i + 1) % CARD_COUNT:03d}"'
        for i in range(CARD_COUNT)
    ]


def _evidence_needles() -> list[str]:
    return [
        (
            f'card "c{i * CARDS_PER_ISLAND:03d}" --evidence:contradicts--> '
            f'card "c{i * CARDS_PER_ISLAND + 1:03d}"'
        )
        for i in range(ISLAND_COUNT)
    ]


def _membership_needles(route: str) -> list[str]:
    needles: list[str] = []
    for island_index in range(ISLAND_COUNT):
        members = [
            f"c{card_index:03d}"
            for card_index in range(
                island_index * CARDS_PER_ISLAND,
                (island_index + 1) * CARDS_PER_ISLAND,
            )
        ]
        if route == "suggest-card-groups":
            needles.append(f'members={",".join(members)})')
        else:
            needles.append(f"cardIds={json.dumps(members)}")
    return needles


def _coordinate_needles() -> list[str]:
    return [f'- card "c{i:03d}" at (' for i in range(CARD_COUNT)]


def _coverage(prompt: str, route: str, *, include_evidence: bool) -> dict[str, Any]:
    source_counts = {
        "card_texts": CARD_COUNT,
        "island_titles": ISLAND_COUNT,
        "complete_island_memberships": ISLAND_COUNT,
        "typed_relations": CARD_COUNT,
        "evidence_links": ISLAND_COUNT if include_evidence else 0,
        "relative_coordinates": CARD_COUNT if route == "suggest-layout" else 0,
    }
    visible = {
        "card_texts": _count(prompt, _card_text_needles()),
        "island_titles": _count(prompt, _island_title_needles()),
        "complete_island_memberships": _count(prompt, _membership_needles(route)),
        "typed_relations": _count(prompt, _relation_needles(route)),
        "evidence_links": _count(prompt, _evidence_needles()) if include_evidence else 0,
        "relative_coordinates": (
            _count(prompt, _coordinate_needles()) if route == "suggest-layout" else 0
        ),
    }
    return {
        "source": source_counts,
        "visible_in_final_prompt": visible,
        "missing_from_final_prompt": {
            key: source_counts[key] - visible[key] for key in source_counts
        },
    }


def _route_result(
    route: str,
    prompt: str,
    ir: dict[str, Any],
    *,
    include_evidence: bool,
) -> dict[str, Any]:
    return {
        "route": route,
        "prompt": {
            "unicode_chars": len(prompt),
            "utf8_bytes": len(prompt.encode("utf-8")),
        },
        "ir": {
            "cards": len(ir.get("cards", [])),
            "islands": len(ir.get("islands", [])),
            "relations": len(ir.get("relations", [])),
            "evidence_links": len(ir.get("evidence_links", [])),
            "coordinates": len(ir.get("coordinates", [])),
            "truncation": ir.get("truncation"),
        },
        "coverage": _coverage(prompt, route, include_evidence=include_evidence),
        "token_measurement": {
            "exact_input_tokens": None,
            "status": "provider-reported-usage-required",
        },
    }


def measure_scenario(*, include_evidence: bool) -> dict[str, Any]:
    doc = representative_document(include_evidence=include_evidence)

    group_payload = SuggestCardGroupsRequest.model_validate(
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
    group_ir = _suggest_card_groups_ir(group_payload)
    candidate_ids, _ = _card_group_candidates(group_payload, group_ir)
    group_prompt = _build_suggest_card_groups_prompt(
        group_payload, group_ir, candidate_ids
    )

    layout_payload = SuggestLayoutRequest.model_validate({"doc": doc})
    layout_ir = _suggest_layout_ir(layout_payload)
    layout_prompt = _build_prompt(layout_payload, layout_ir)

    narrative_payload = GenerateNarrativeRequest.model_validate({"doc": doc})
    narrative_ir = _generate_narrative_ir(narrative_payload)
    narrative_prompt = _build_generate_narrative_prompt(narrative_payload, narrative_ir)

    return {
        "scenario": (
            "300-cards-30-islands-ring-with-evidence"
            if include_evidence
            else "300-cards-30-islands-ring"
        ),
        "routes": {
            "suggest-card-groups": _route_result(
                "suggest-card-groups",
                group_prompt,
                group_ir,
                include_evidence=include_evidence,
            ),
            "suggest-layout": _route_result(
                "suggest-layout",
                layout_prompt,
                layout_ir,
                include_evidence=include_evidence,
            ),
            "generate-narrative": _route_result(
                "generate-narrative",
                narrative_prompt,
                narrative_ir,
                include_evidence=include_evidence,
            ),
        },
    }


def measure() -> dict[str, Any]:
    return {
        "measurement": "ai-route-final-prompt-coverage",
        "scenarios": {
            "base": measure_scenario(include_evidence=False),
            "with_evidence": measure_scenario(include_evidence=True),
        },
        "interpretation_boundary": (
            "Coverage describes deterministic rendered prompts only. It does not "
            "measure model quality, task success, or exact provider token usage."
        ),
    }


def main() -> int:
    print(json.dumps(measure(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
