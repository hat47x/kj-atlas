#!/usr/bin/env python3
"""Characterize how hierarchical layout-C outputs compose back into one layout.

R25 proved that the 300-card representative document can be partitioned into
30 island-local layout prompts plus one global-alignment prompt without losing
cards or typed relations. R26 made those prompts measurable with an explicit
provider opt-in. This module closes a different, deterministic question: if all
31 stages return structurally valid outputs, can they be combined into one
complete card layout without silently dropping or inventing ids?

This is measurement-only code. It does not call an LLM and does not change the
production ``/ai/suggest-layout`` route. Synthetic responses are used to prove
composition algebra and fail-closed boundaries only; they say nothing about
model quality.
"""

from __future__ import annotations

import json
import math
from copy import deepcopy
from typing import Any

try:
    from scripts.measure_ai_layout_hierarchical_candidate import (
        build_hierarchical_layout_candidate,
    )
    from scripts.measure_ai_route_projection_candidates import _late_layout_document
except ModuleNotFoundError as exc:
    if exc.name != "scripts":
        raise
    from measure_ai_layout_hierarchical_candidate import (
        build_hierarchical_layout_candidate,
    )
    from measure_ai_route_projection_candidates import _late_layout_document


def _number(value: Any, *, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be a number")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{field} must be finite")
    return result


def _cards_by_id(doc: dict[str, Any]) -> dict[str, dict[str, Any]]:
    cards: dict[str, dict[str, Any]] = {}
    for card in doc.get("cards", []):
        card_id = card.get("id")
        if not isinstance(card_id, str) or not card_id:
            raise ValueError("source card must have a non-empty id")
        if card_id in cards:
            raise ValueError("source contains duplicate card id")
        cards[card_id] = card
    return cards


def _batch_centroid(
    batch: dict[str, Any], cards_by_id: dict[str, dict[str, Any]]
) -> tuple[float, float]:
    card_ids = batch["card_ids"]
    if not card_ids:
        raise ValueError("layout batch must contain at least one card")
    xs = [_number(cards_by_id[card_id].get("x"), field="source card x") for card_id in card_ids]
    ys = [_number(cards_by_id[card_id].get("y"), field="source card y") for card_id in card_ids]
    return sum(xs) / len(xs), sum(ys) / len(ys)


def build_identity_results(
    doc: dict[str, Any], plan: dict[str, Any]
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    """Return synthetic local/global outputs that encode the source layout exactly."""
    cards = _cards_by_id(doc)
    local: dict[str, dict[str, Any]] = {}
    global_rows: list[dict[str, Any]] = []

    for batch in plan["batches"]:
        batch_id = batch["batch_id"]
        cx, cy = _batch_centroid(batch, cards)
        local[batch_id] = {
            "batchId": batch_id,
            "cards": [
                {
                    "id": card_id,
                    "dx": _number(cards[card_id].get("x"), field="source card x") - cx,
                    "dy": _number(cards[card_id].get("y"), field="source card y") - cy,
                }
                for card_id in batch["card_ids"]
            ],
            "notes": "synthetic identity fixture",
        }
        global_rows.append(
            {
                "batchId": batch_id,
                "anchorX": cx,
                "anchorY": cy,
            }
        )

    return local, {"batches": global_rows, "notes": "synthetic identity fixture"}


def _parse_local_result(
    raw: dict[str, Any], *, expected_batch: dict[str, Any]
) -> dict[str, tuple[float, float]]:
    if not isinstance(raw, dict):
        raise ValueError("local result must be an object")
    if raw.get("batchId") != expected_batch["batch_id"]:
        raise ValueError("local result batchId mismatch")

    rows = raw.get("cards")
    if not isinstance(rows, list):
        raise ValueError("local result cards must be a list")

    expected_ids = list(expected_batch["card_ids"])
    expected_set = set(expected_ids)
    if len(rows) != len(expected_ids):
        raise ValueError("local result must include every batch card exactly once")

    parsed: dict[str, tuple[float, float]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("local card result must be an object")
        card_id = row.get("id")
        if not isinstance(card_id, str):
            raise ValueError("local card result must include id")
        if card_id not in expected_set:
            raise ValueError("local result included unknown card id")
        if card_id in parsed:
            raise ValueError("local result included duplicate card id")
        parsed[card_id] = (
            _number(row.get("dx"), field="local dx"),
            _number(row.get("dy"), field="local dy"),
        )

    if set(parsed) != expected_set:
        raise ValueError("local result must include every batch card exactly once")
    return parsed


def _parse_global_result(
    raw: dict[str, Any], *, expected_batches: list[dict[str, Any]]
) -> dict[str, tuple[float, float]]:
    if not isinstance(raw, dict):
        raise ValueError("global result must be an object")
    rows = raw.get("batches")
    if not isinstance(rows, list):
        raise ValueError("global result batches must be a list")

    expected_ids = [batch["batch_id"] for batch in expected_batches]
    expected_set = set(expected_ids)
    if len(rows) != len(expected_ids):
        raise ValueError("global result must include every batch exactly once")

    parsed: dict[str, tuple[float, float]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("global batch result must be an object")
        batch_id = row.get("batchId")
        if not isinstance(batch_id, str):
            raise ValueError("global batch result must include batchId")
        if batch_id not in expected_set:
            raise ValueError("global result included unknown batch id")
        if batch_id in parsed:
            raise ValueError("global result included duplicate batch id")
        parsed[batch_id] = (
            _number(row.get("anchorX"), field="global anchorX"),
            _number(row.get("anchorY"), field="global anchorY"),
        )

    if set(parsed) != expected_set:
        raise ValueError("global result must include every batch exactly once")
    return parsed


def compose_hierarchical_layout(
    doc: dict[str, Any],
    plan: dict[str, Any],
    local_results: dict[str, dict[str, Any]],
    global_result: dict[str, Any],
) -> dict[str, Any]:
    """Compose validated local offsets with validated global batch anchors.

    The final card coordinate is ``anchor + local offset``. The source transform
    is preserved unchanged: the measurement candidate moves document content,
    not the user's viewport, and therefore does not invent a pan/zoom decision.
    """
    batches = plan["batches"]
    expected_batch_ids = {batch["batch_id"] for batch in batches}
    if set(local_results) != expected_batch_ids:
        raise ValueError("local result set must match layout batches exactly")

    anchors = _parse_global_result(global_result, expected_batches=batches)
    source_cards = _cards_by_id(doc)
    composed: dict[str, dict[str, Any]] = {}

    for batch in batches:
        batch_id = batch["batch_id"]
        offsets = _parse_local_result(local_results[batch_id], expected_batch=batch)
        anchor_x, anchor_y = anchors[batch_id]
        for card_id in batch["card_ids"]:
            if card_id in composed:
                raise ValueError("composition assigned a card more than once")
            dx, dy = offsets[card_id]
            composed[card_id] = {
                "id": card_id,
                "x": anchor_x + dx,
                "y": anchor_y + dy,
            }

    if set(composed) != set(source_cards):
        raise ValueError("composition must cover every source card exactly once")

    transform = deepcopy(doc.get("transform", {"panX": 0.0, "panY": 0.0, "zoom": 1.0}))
    return {
        "transform": transform,
        "cards": [composed[card_id] for card_id in sorted(composed)],
        "notes": "measurement-only hierarchical composition",
    }


def _position_map(layout: dict[str, Any]) -> dict[str, tuple[float, float]]:
    return {
        row["id"]: (
            _number(row.get("x"), field="composed x"),
            _number(row.get("y"), field="composed y"),
        )
        for row in layout["cards"]
    }


def _source_position_map(doc: dict[str, Any]) -> dict[str, tuple[float, float]]:
    return {
        card_id: (
            _number(card.get("x"), field="source card x"),
            _number(card.get("y"), field="source card y"),
        )
        for card_id, card in _cards_by_id(doc).items()
    }


def _max_axis_error(
    actual: dict[str, tuple[float, float]],
    expected: dict[str, tuple[float, float]],
) -> tuple[float, float]:
    if set(actual) != set(expected):
        raise ValueError("position maps must contain identical ids")
    x_error = max((abs(actual[card_id][0] - expected[card_id][0]) for card_id in actual), default=0.0)
    y_error = max((abs(actual[card_id][1] - expected[card_id][1]) for card_id in actual), default=0.0)
    return x_error, y_error


def measure() -> dict[str, Any]:
    doc = _late_layout_document()
    plan = build_hierarchical_layout_candidate(doc)
    local, global_result = build_identity_results(doc, plan)

    identity = compose_hierarchical_layout(doc, plan, local, global_result)
    identity_positions = _position_map(identity)
    source_positions = _source_position_map(doc)
    identity_x_error, identity_y_error = _max_axis_error(identity_positions, source_positions)

    translated_global = deepcopy(global_result)
    shift_x, shift_y = 250.0, -125.0
    for row in translated_global["batches"]:
        row["anchorX"] += shift_x
        row["anchorY"] += shift_y
    translated = compose_hierarchical_layout(doc, plan, local, translated_global)
    translated_positions = _position_map(translated)
    translated_expected = {
        card_id: (x + shift_x, y + shift_y)
        for card_id, (x, y) in source_positions.items()
    }
    translation_x_error, translation_y_error = _max_axis_error(
        translated_positions, translated_expected
    )

    perturbed_local = deepcopy(local)
    target_card = "c299"
    target_batch = next(
        batch["batch_id"] for batch in plan["batches"] if target_card in batch["card_ids"]
    )
    target_row = next(
        row for row in perturbed_local[target_batch]["cards"] if row["id"] == target_card
    )
    local_shift_x, local_shift_y = 7.5, -3.25
    target_row["dx"] += local_shift_x
    target_row["dy"] += local_shift_y
    perturbed = compose_hierarchical_layout(doc, plan, perturbed_local, global_result)
    perturbed_positions = _position_map(perturbed)
    moved_ids = sorted(
        card_id
        for card_id in source_positions
        if perturbed_positions[card_id] != source_positions[card_id]
    )
    expected_target = (
        source_positions[target_card][0] + local_shift_x,
        source_positions[target_card][1] + local_shift_y,
    )
    target_x_error = abs(perturbed_positions[target_card][0] - expected_target[0])
    target_y_error = abs(perturbed_positions[target_card][1] - expected_target[1])

    return {
        "measurement": "ai-layout-hierarchical-composition-contract",
        "scenario": "300-cards-30-islands-ring-with-synthetic-stage-results",
        "source": {
            "cards": len(doc["cards"]),
            "batches": len(plan["batches"]),
            "transform": deepcopy(doc.get("transform")),
        },
        "identity_round_trip": {
            "composed_cards": len(identity["cards"]),
            "all_source_ids_preserved": set(identity_positions) == set(source_positions),
            "max_abs_x_error": identity_x_error,
            "max_abs_y_error": identity_y_error,
            "source_transform_preserved": identity["transform"] == doc.get("transform"),
        },
        "global_translation_probe": {
            "shift": {"x": shift_x, "y": shift_y},
            "moved_cards": sum(
                translated_positions[card_id] != source_positions[card_id]
                for card_id in source_positions
            ),
            "max_abs_x_error_from_expected_translation": translation_x_error,
            "max_abs_y_error_from_expected_translation": translation_y_error,
        },
        "local_perturbation_probe": {
            "target_card": target_card,
            "target_batch": target_batch,
            "local_shift": {"dx": local_shift_x, "dy": local_shift_y},
            "moved_ids": moved_ids,
            "target_x_error": target_x_error,
            "target_y_error": target_y_error,
        },
        "validation_boundary": [
            "local response set must equal the batch set",
            "each local response must contain every batch card exactly once",
            "global response must contain every batch anchor exactly once",
            "unknown or duplicate card/batch ids fail closed",
            "all offsets, anchors, and composed coordinates must be finite numbers",
            "composition must cover every source card exactly once",
            "source transform is preserved rather than invented by the hierarchy",
        ],
        "interpretation_boundary": (
            "Synthetic stage outputs only: this proves deterministic composition and structural "
            "completeness, not provider/model layout quality, latency, token cost, or the quality "
            "of any generated local offsets/global anchors. No external provider is called."
        ),
    }


def main() -> int:
    print(json.dumps(measure(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
