#!/usr/bin/env python3
"""Characterize a deterministic hierarchical (C) layout candidate at 300-card scale.

`AI-IR-SCALE-01` R21 leaves hierarchical/batched layout as option C when a
one-shot full projection is too close to a named provider/model's input budget.
This script makes that option concrete without changing production routing or
calling an LLM.

The representative 300-card / 30-island layout is split into two semantic
levels:

1. island-local batches: every direct member card appears in exactly one local
   batch with its current local geometry and every card relation whose endpoints
   are in that same batch;
2. one global alignment batch: every island (and any lone-card batch) becomes a
   node, while every relation crossing local-batch boundaries is carried as an
   explicit bridge that retains the source card ids and relation type.

The point is not to claim that this is the final production algorithm.  It is a
measurement-only candidate for answering three deterministic questions before
provider token measurements are available:

- can all cards be assigned exactly once without global centrality truncation?
- can every typed relation be represented exactly once as either local or a
  cross-batch bridge?
- how does the largest single prompt compare with the one-shot route-B prompt?

Prompt bytes/chars are diagnostic only.  They are never converted to token
counts; exact token counts remain provider-reported usage only.
"""

from __future__ import annotations

import json
from collections import defaultdict
from typing import Any

from kj_atlas_api.models import SuggestLayoutRequest
from kj_atlas_api.routes.ai import _build_prompt

try:
    from scripts.measure_ai_route_projection_candidates import (
        _late_layout_document,
        _layout_candidate_context,
    )
except ModuleNotFoundError as exc:
    if exc.name != "scripts":
        raise
    from measure_ai_route_projection_candidates import (
        _late_layout_document,
        _layout_candidate_context,
    )


def _prompt_size(prompt: str) -> dict[str, int]:
    return {
        "unicode_chars": len(prompt),
        "utf8_bytes": len(prompt.encode("utf-8")),
    }


def _edge_kind(edge: dict[str, Any], side: str) -> str:
    value = edge.get(f"{side}Kind")
    return value if isinstance(value, str) and value else "card"


def _batch_ownership(doc: dict[str, Any]) -> tuple[dict[str, str], dict[str, dict[str, Any]]]:
    """Assign each card to one deterministic direct-membership batch.

    Multiple direct island memberships are rejected instead of silently picking
    one owner.  A card outside every island becomes its own lone-card batch so
    coverage remains total rather than dropping peripheral observations.
    """
    cards_by_id = {card["id"]: card for card in doc["cards"]}
    owners: dict[str, str] = {}
    batch_meta: dict[str, dict[str, Any]] = {}

    for island in sorted(doc["islands"], key=lambda item: item["id"]):
        batch_id = f'island:{island["id"]}'
        members = sorted(island.get("cardIds", []))
        batch_meta[batch_id] = {
            "batch_id": batch_id,
            "kind": "island",
            "source_id": island["id"],
            "title": island.get("title") or "",
            "parent_island_id": island.get("parentIslandId"),
            "card_ids": members,
        }
        for card_id in members:
            if card_id not in cards_by_id:
                raise ValueError("island membership references an unknown card")
            if card_id in owners:
                raise ValueError("card belongs to multiple direct island batches")
            owners[card_id] = batch_id

    for card_id in sorted(cards_by_id):
        if card_id in owners:
            continue
        batch_id = f"lone:{card_id}"
        owners[card_id] = batch_id
        batch_meta[batch_id] = {
            "batch_id": batch_id,
            "kind": "lone_card",
            "source_id": card_id,
            "title": "",
            "parent_island_id": None,
            "card_ids": [card_id],
        }

    return owners, batch_meta


def _relation_partition(
    doc: dict[str, Any], owners: dict[str, str]
) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    """Put every relation in exactly one local or global bucket."""
    local: dict[str, list[dict[str, Any]]] = defaultdict(list)
    global_relations: list[dict[str, Any]] = []

    edges = sorted(
        doc.get("edges", []),
        key=lambda edge: (
            str(edge.get("type", "")),
            str(edge.get("fromId", "")),
            str(edge.get("toId", "")),
            str(edge.get("id", "")),
        ),
    )
    for edge in edges:
        from_kind = _edge_kind(edge, "from")
        to_kind = _edge_kind(edge, "to")
        row = {
            "id": edge.get("id"),
            "type": edge.get("type"),
            "from_kind": from_kind,
            "from_id": edge.get("fromId"),
            "to_kind": to_kind,
            "to_id": edge.get("toId"),
        }

        if from_kind == "card" and to_kind == "card":
            from_batch = owners.get(str(edge.get("fromId")))
            to_batch = owners.get(str(edge.get("toId")))
            if from_batch is None or to_batch is None:
                raise ValueError("card relation references an unknown card")
            if from_batch == to_batch:
                row["batch_id"] = from_batch
                local[from_batch].append(row)
                continue
            row["from_batch"] = from_batch
            row["to_batch"] = to_batch

        # Cross-card relations and any explicit island/mixed relation are global
        # structure.  Nothing is discarded merely because it crosses a batch.
        global_relations.append(row)

    return dict(local), global_relations


def _centroid(cards: list[dict[str, Any]]) -> tuple[float, float]:
    if not cards:
        return 0.0, 0.0
    return (
        sum(float(card.get("x", 0.0)) for card in cards) / len(cards),
        sum(float(card.get("y", 0.0)) for card in cards) / len(cards),
    )


def _local_prompt(
    batch: dict[str, Any],
    *,
    cards_by_id: dict[str, dict[str, Any]],
    relations: list[dict[str, Any]],
) -> str:
    cards = [cards_by_id[card_id] for card_id in batch["card_ids"]]
    cx, cy = _centroid(cards)
    card_lines = [
        (
            f'- id="{card["id"]}", text={json.dumps(card["text"], ensure_ascii=False)}, '
            f'localX={float(card.get("x", 0.0)) - cx:.4f}, '
            f'localY={float(card.get("y", 0.0)) - cy:.4f}'
        )
        for card in cards
    ]
    relation_lines = [
        f'- card "{row["from_id"]}" --{row["type"]}--> card "{row["to_id"]}"'
        for row in relations
    ]
    return "\n".join(
        [
            "You are generating one local component of a hierarchical draft layout.",
            "This is advisory only. Do not alter card text or ids.",
            "Use only the cards in this batch. Return offsets around this batch's own origin.",
            "Do not infer global canvas position here; a separate global alignment stage owns that decision.",
            "Return strict JSON only. No markdown.",
            'Use schema: {"batchId":string,"cards":[{"id":string,"dx":number,"dy":number}],"notes":string?}',
            f'Batch id="{batch["batch_id"]}", kind="{batch["kind"]}", sourceId="{batch["source_id"]}"',
            "Cards:",
            *card_lines,
            "Relations internal to this batch:",
            *(relation_lines or ["- (none)"]),
        ]
    )


def _global_prompt(
    batches: list[dict[str, Any]],
    *,
    cards_by_id: dict[str, dict[str, Any]],
    relations: list[dict[str, Any]],
) -> str:
    batch_lines: list[str] = []
    for batch in batches:
        cards = [cards_by_id[card_id] for card_id in batch["card_ids"]]
        cx, cy = _centroid(cards)
        batch_lines.append(
            f'- batch="{batch["batch_id"]}", kind="{batch["kind"]}", '
            f'sourceId="{batch["source_id"]}", title={json.dumps(batch["title"], ensure_ascii=False)}, '
            f'memberCount={len(batch["card_ids"])}, currentAnchor=({cx:.4f},{cy:.4f}), '
            f'parentIslandId={json.dumps(batch["parent_island_id"], ensure_ascii=False)}'
        )

    relation_lines: list[str] = []
    for row in relations:
        if row["from_kind"] == "card" and row["to_kind"] == "card":
            relation_lines.append(
                f'- bridge type="{row["type"]}": batch "{row["from_batch"]}" '
                f'(card "{row["from_id"]}") -> batch "{row["to_batch"]}" '
                f'(card "{row["to_id"]}")'
            )
        else:
            relation_lines.append(
                f'- stated type="{row["type"]}": {row["from_kind"]} "{row["from_id"]}" '
                f'-> {row["to_kind"]} "{row["to_id"]}"'
            )

    return "\n".join(
        [
            "You are aligning already-solved local layout batches into one global draft layout.",
            "This is advisory only. Do not rewrite or merge batches.",
            "Choose one anchor per batch. Local card offsets are composed with these anchors afterwards.",
            "Use every cross-batch bridge below; do not invent relations that are not listed.",
            "Keep negate bridges visibly separated and connected/causal bridges legible without collapsing distinct batches.",
            "Return strict JSON only. No markdown.",
            'Use schema: {"batches":[{"batchId":string,"anchorX":number,"anchorY":number}],"notes":string?}',
            "Batches:",
            *batch_lines,
            "Cross-batch / stated relations:",
            *(relation_lines or ["- (none)"]),
        ]
    )


def build_hierarchical_layout_candidate(doc: dict[str, Any]) -> dict[str, Any]:
    """Return a canonical measurement plan and prompts for option C."""
    cards_by_id = {card["id"]: card for card in doc["cards"]}
    owners, batch_meta = _batch_ownership(doc)
    local_relations, global_relations = _relation_partition(doc, owners)

    batches = [batch_meta[batch_id] for batch_id in sorted(batch_meta)]
    local_prompts: list[dict[str, Any]] = []
    for batch in batches:
        rows = local_relations.get(batch["batch_id"], [])
        prompt = _local_prompt(batch, cards_by_id=cards_by_id, relations=rows)
        local_prompts.append(
            {
                "batch_id": batch["batch_id"],
                "card_ids": list(batch["card_ids"]),
                "relation_ids": [row["id"] for row in rows],
                "prompt": prompt,
                "prompt_size": _prompt_size(prompt),
            }
        )

    global_prompt = _global_prompt(
        batches,
        cards_by_id=cards_by_id,
        relations=global_relations,
    )

    local_relation_ids = [
        relation_id
        for item in local_prompts
        for relation_id in item["relation_ids"]
    ]
    global_relation_ids = [row["id"] for row in global_relations]
    assigned_cards = [card_id for item in local_prompts for card_id in item["card_ids"]]

    return {
        "batches": batches,
        "local_prompts": local_prompts,
        "global_prompt": global_prompt,
        "global_prompt_size": _prompt_size(global_prompt),
        "global_relations": global_relations,
        "coverage": {
            "source_cards": len(cards_by_id),
            "assigned_cards": len(assigned_cards),
            "unique_assigned_cards": len(set(assigned_cards)),
            "source_relations": len(doc.get("edges", [])),
            "local_relations": len(local_relation_ids),
            "global_relations": len(global_relation_ids),
            "unique_relation_ids": len(set(local_relation_ids + global_relation_ids)),
            "source_islands": len(doc.get("islands", [])),
            "island_batches": sum(batch["kind"] == "island" for batch in batches),
            "lone_card_batches": sum(batch["kind"] == "lone_card" for batch in batches),
        },
    }


def measure() -> dict[str, Any]:
    doc = _late_layout_document()
    plan = build_hierarchical_layout_candidate(doc)

    # R23's one-shot route-B prompt is the apples-to-apples full-coverage layout
    # candidate.  Keep it beside C so the largest single request can be compared
    # before provider-reported token counts are available.
    payload = SuggestLayoutRequest.model_validate({"doc": doc})
    route_b_context = _layout_candidate_context(payload)
    route_b_prompt = _build_prompt(payload, route_b_context)

    local_sizes = [item["prompt_size"]["utf8_bytes"] for item in plan["local_prompts"]]
    global_bytes = plan["global_prompt_size"]["utf8_bytes"]
    all_request_bytes = [*local_sizes, global_bytes]

    tail_local = next(
        item for item in plan["local_prompts"] if "c299" in item["card_ids"]
    )
    tail_global = [
        row
        for row in plan["global_relations"]
        if row.get("from_id") == "c299" and row.get("to_id") == "c000"
    ]

    return {
        "measurement": "ai-layout-hierarchical-candidate-at-scale",
        "scenario": "300-cards-30-islands-ring-with-tail-causal-negate",
        "source": {
            "cards": len(doc["cards"]),
            "islands": len(doc["islands"]),
            "relations": len(doc["edges"]),
        },
        "route_b_one_shot": {
            "requests": 1,
            "prompt": _prompt_size(route_b_prompt),
        },
        "hierarchical_c_candidate": {
            "requests": len(plan["local_prompts"]) + 1,
            "local_batches": len(plan["local_prompts"]),
            "max_cards_per_local_batch": max(
                len(item["card_ids"]) for item in plan["local_prompts"]
            ),
            "coverage": plan["coverage"],
            "prompt_bytes": {
                "max_single_request": max(all_request_bytes),
                "min_local_request": min(local_sizes),
                "max_local_request": max(local_sizes),
                "sum_local_requests": sum(local_sizes),
                "global_alignment_request": global_bytes,
                "aggregate_all_requests": sum(all_request_bytes),
            },
            "tail_checks": {
                "c298_c299_same_local_batch": (
                    "c298" in tail_local["card_ids"] and "c299" in tail_local["card_ids"]
                ),
                "tail_local_relation_ids": tail_local["relation_ids"],
                "c299_c000_cross_bridge_count": len(tail_global),
                "c299_c000_cross_bridge_types": [row["type"] for row in tail_global],
            },
        },
        "interpretation_boundary": (
            "Measurement-only hierarchical layout candidate. Every relation is assigned exactly once "
            "to a local batch or global bridge. Prompt chars/bytes are diagnostics, not token counts. "
            "No production route, IR cap, SafeMode, proposal-only boundary, or provider call changes."
        ),
    }


def main() -> int:
    print(json.dumps(measure(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
