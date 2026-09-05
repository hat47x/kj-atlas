from __future__ import annotations

import json
import math
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest

from scripts import measure_ai_layout_hierarchical_composition as composition
from scripts.measure_ai_layout_hierarchical_candidate import (
    build_hierarchical_layout_candidate,
)
from scripts.measure_ai_route_projection_candidates import _late_layout_document


def _identity_fixture():
    doc = _late_layout_document()
    plan = build_hierarchical_layout_candidate(doc)
    local, global_result = composition.build_identity_results(doc, plan)
    return doc, plan, local, global_result


def test_identity_composition_round_trips_all_300_cards_and_preserves_transform() -> None:
    report = composition.measure()
    identity = report["identity_round_trip"]

    assert report["source"]["cards"] == 300
    assert report["source"]["batches"] == 30
    assert identity["composed_cards"] == 300
    assert identity["all_source_ids_preserved"] is True
    assert identity["max_abs_x_error"] <= 1e-9
    assert identity["max_abs_y_error"] <= 1e-9
    assert identity["source_transform_preserved"] is True
    assert "No external provider is called" in report["interpretation_boundary"]


def test_global_anchor_translation_moves_every_card_by_exactly_the_same_vector() -> None:
    probe = composition.measure()["global_translation_probe"]

    assert probe["shift"] == {"x": 250.0, "y": -125.0}
    assert probe["moved_cards"] == 300
    assert probe["max_abs_x_error_from_expected_translation"] <= 1e-9
    assert probe["max_abs_y_error_from_expected_translation"] <= 1e-9


def test_local_offset_perturbation_moves_only_its_card() -> None:
    probe = composition.measure()["local_perturbation_probe"]

    assert probe["target_card"] == "c299"
    assert probe["target_batch"] == "island:i29"
    assert probe["local_shift"] == {"dx": 7.5, "dy": -3.25}
    assert probe["moved_ids"] == ["c299"]
    assert probe["target_x_error"] <= 1e-9
    assert probe["target_y_error"] <= 1e-9


def test_composed_layout_has_all_source_ids_once_in_deterministic_order() -> None:
    doc, plan, local, global_result = _identity_fixture()

    result = composition.compose_hierarchical_layout(doc, plan, local, global_result)
    ids = [card["id"] for card in result["cards"]]

    assert ids == sorted(card["id"] for card in doc["cards"])
    assert len(ids) == len(set(ids)) == 300
    assert result["transform"] == doc["transform"]


def test_source_order_reversal_does_not_change_identity_composition() -> None:
    doc = _late_layout_document()
    reversed_doc = deepcopy(doc)
    reversed_doc["cards"] = list(reversed(reversed_doc["cards"]))
    reversed_doc["islands"] = list(reversed(reversed_doc["islands"]))
    reversed_doc["edges"] = list(reversed(reversed_doc["edges"]))

    first_plan = build_hierarchical_layout_candidate(doc)
    second_plan = build_hierarchical_layout_candidate(reversed_doc)
    first_local, first_global = composition.build_identity_results(doc, first_plan)
    second_local, second_global = composition.build_identity_results(
        reversed_doc, second_plan
    )

    first = composition.compose_hierarchical_layout(
        doc, first_plan, first_local, first_global
    )
    second = composition.compose_hierarchical_layout(
        reversed_doc, second_plan, second_local, second_global
    )

    assert first == second


def test_lone_card_batch_composes_instead_of_disappearing() -> None:
    doc = _late_layout_document()
    doc["islands"][0]["cardIds"].remove("c000")
    plan = build_hierarchical_layout_candidate(doc)
    local, global_result = composition.build_identity_results(doc, plan)

    result = composition.compose_hierarchical_layout(doc, plan, local, global_result)
    positions = {card["id"]: (card["x"], card["y"]) for card in result["cards"]}
    source = {card["id"]: (card["x"], card["y"]) for card in doc["cards"]}

    assert "lone:c000" in local
    assert len(result["cards"]) == 300
    assert math.isclose(positions["c000"][0], source["c000"][0], abs_tol=1e-9)
    assert math.isclose(positions["c000"][1], source["c000"][1], abs_tol=1e-9)


def test_missing_or_extra_local_batch_response_fails_closed() -> None:
    doc, plan, local, global_result = _identity_fixture()
    missing = deepcopy(local)
    missing.pop("island:i29")

    with pytest.raises(ValueError, match="local result set must match"):
        composition.compose_hierarchical_layout(doc, plan, missing, global_result)

    extra = deepcopy(local)
    extra["island:unknown"] = {"batchId": "island:unknown", "cards": []}
    with pytest.raises(ValueError, match="local result set must match"):
        composition.compose_hierarchical_layout(doc, plan, extra, global_result)


def test_local_card_ids_must_be_complete_unique_and_known() -> None:
    doc, plan, local, global_result = _identity_fixture()

    duplicate = deepcopy(local)
    duplicate["island:i29"]["cards"][-1]["id"] = duplicate["island:i29"]["cards"][0]["id"]
    with pytest.raises(ValueError, match="duplicate card id|every batch card"):
        composition.compose_hierarchical_layout(doc, plan, duplicate, global_result)

    unknown = deepcopy(local)
    unknown["island:i29"]["cards"][-1]["id"] = "unknown-card"
    with pytest.raises(ValueError, match="unknown card id"):
        composition.compose_hierarchical_layout(doc, plan, unknown, global_result)


def test_global_batch_ids_must_be_complete_unique_and_known() -> None:
    doc, plan, local, global_result = _identity_fixture()

    missing = deepcopy(global_result)
    missing["batches"].pop()
    with pytest.raises(ValueError, match="every batch exactly once"):
        composition.compose_hierarchical_layout(doc, plan, local, missing)

    duplicate = deepcopy(global_result)
    duplicate["batches"][-1]["batchId"] = duplicate["batches"][0]["batchId"]
    with pytest.raises(ValueError, match="duplicate batch id|every batch"):
        composition.compose_hierarchical_layout(doc, plan, local, duplicate)


def test_non_finite_local_or_global_values_fail_closed() -> None:
    doc, plan, local, global_result = _identity_fixture()

    bad_local = deepcopy(local)
    bad_local["island:i29"]["cards"][0]["dx"] = float("nan")
    with pytest.raises(ValueError, match="local dx must be finite"):
        composition.compose_hierarchical_layout(doc, plan, bad_local, global_result)

    bad_global = deepcopy(global_result)
    bad_global["batches"][0]["anchorX"] = float("inf")
    with pytest.raises(ValueError, match="global anchorX must be finite"):
        composition.compose_hierarchical_layout(doc, plan, local, bad_global)


def test_documented_direct_cli_runs_without_network_access() -> None:
    backend_dir = Path(__file__).resolve().parents[1]
    completed = subprocess.run(
        [sys.executable, "scripts/measure_ai_layout_hierarchical_composition.py"],
        cwd=backend_dir,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)

    assert report["measurement"] == "ai-layout-hierarchical-composition-contract"
    assert report["identity_round_trip"]["composed_cards"] == 300
    assert report["identity_round_trip"]["max_abs_x_error"] <= 1e-9
    assert report["identity_round_trip"]["max_abs_y_error"] <= 1e-9
