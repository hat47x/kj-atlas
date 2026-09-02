#!/usr/bin/env python3
"""Measure the representative-scale LLM input IR without calling an LLM.

AI-IR-PROJECTION-01 AC-10 asks for a roughly 300-card / 30-island scale
measurement before Stage 5 broadens IR adoption.  This script deliberately
measures the deterministic projection boundary first:

- 300 reviewed cards;
- 30 islands, 10 cards each;
- 300 card-to-card relations in one ring;
- optional coordinates, matching the heaviest migrated route (suggest-layout).

The provider transport sends a rendered prompt, not ``LLMRequest.inputs``
directly, and the repository supports more than one model/provider.  Therefore
this script does *not* invent a provider-independent token count.  It records
exact compact-JSON characters/UTF-8 bytes and structural loss.  Exact input
tokens must be recorded from provider-reported usage for a named model.
"""

from __future__ import annotations

import argparse
import json
from typing import Any

from kj_atlas_api.llm_input_ir import (
    IRSource,
    SourceCard,
    SourceIsland,
    SourceRelation,
    build_llm_input_ir,
)

CARD_COUNT = 300
ISLAND_COUNT = 30
CARDS_PER_ISLAND = 10


def representative_source() -> IRSource:
    cards = tuple(
        SourceCard(
            id=f"c{i:03d}",
            text=(
                f"観察{i:03d}: 根拠・異論・保留を失わず、"
                "後から判断の経路へ戻れるように残した代表規模カード。"
            ),
            text_reviewed=True,
            x=float(i % 30),
            y=float(i // 30),
        )
        for i in range(CARD_COUNT)
    )
    islands = tuple(
        SourceIsland(
            id=f"i{i:02d}",
            card_ids=tuple(
                f"c{card_index:03d}"
                for card_index in range(i * CARDS_PER_ISLAND, (i + 1) * CARDS_PER_ISLAND)
            ),
            title=f"島{i:02d}",
            title_reviewed=True,
        )
        for i in range(ISLAND_COUNT)
    )
    relations = tuple(
        SourceRelation(
            from_id=f"c{i:03d}",
            to_id=f"c{(i + 1) % CARD_COUNT:03d}",
            type="related",
        )
        for i in range(CARD_COUNT)
    )
    return IRSource(
        doc_id="representative-scale-300x30",
        doc_version=1,
        cards=cards,
        relations=relations,
        islands=islands,
    )


def measure(*, include_coordinates: bool) -> dict[str, Any]:
    source = representative_source()
    ir = build_llm_input_ir(source, include_coordinates=include_coordinates)
    compact = json.dumps(ir, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    projected_card_ids = {card["id"] for card in ir["cards"]}
    source_card_ids = {card.id for card in source.cards}
    empty_islands = [island["id"] for island in ir.get("islands", []) if not island["card_ids"]]

    return {
        "scenario": "300-cards-30-islands-ring",
        "include_coordinates": include_coordinates,
        "source": {
            "cards": len(source.cards),
            "islands": len(source.islands),
            "relations": len(source.relations),
            "text_chars": sum(len(card.text) for card in source.cards),
        },
        "projected": {
            "cards": len(ir["cards"]),
            "islands": len(ir.get("islands", [])),
            "empty_islands": len(empty_islands),
            "empty_island_ids": empty_islands,
            "relations": len(ir["relations"]),
            "coordinates": len(ir.get("coordinates", [])),
            "dropped_cards": len(source_card_ids - projected_card_ids),
        },
        "truncation": ir["truncation"],
        "serialized": {
            "unicode_chars": len(compact),
            "utf8_bytes": len(compact.encode("utf-8")),
        },
        "token_measurement": {
            "exact_input_tokens": None,
            "status": "provider-reported-usage-required",
            "reason": (
                "The provider receives a rendered prompt and tokenization is model-specific; "
                "do not infer exact input_tokens from IR bytes."
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--with-coordinates",
        action="store_true",
        help="measure the heaviest IR projection used by suggest-layout",
    )
    args = parser.parse_args()
    print(json.dumps(measure(include_coordinates=args.with_coordinates), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
