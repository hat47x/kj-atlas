from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

import kj_atlas_api.llm_input_ir as ir_module
from scripts import measure_ai_route_a2_candidate as a2
from scripts.measure_ai_route_projection_candidates import _late_layout_document


def test_representative_fit_is_exact_lower_bound_not_production_cap() -> None:
    budget = a2.representative_fit_budget(_late_layout_document())

    assert budget == {
        "max_cards": 300,
        "max_text_chars": 13_800,
        "max_relations": 400,
    }
    assert ir_module.MAX_CARDS == 200
    assert ir_module.MAX_TEXT_CHARS == 12_000
    assert ir_module.MAX_RELATIONS == 400


def test_a2_candidate_restores_full_groups_required_coverage_and_caps() -> None:
    report = a2.measure()
    groups = report["groups"]
    candidate = groups["a2_lower_bound_candidate"]

    assert groups["production_caps_restored"] is True
    assert groups["production_caps"] == {
        "max_cards": 200,
        "max_text_chars": 12_000,
        "max_relations": 400,
    }
    assert candidate["projected_cards"] == 300
    assert candidate["relations"] == 300
    assert candidate["complete_island_memberships"] == 30
    assert candidate["groupable_candidates"] == 299
    assert candidate["withheld_held_cards"] == 1
    assert candidate["truncation"] == {"truncated": False, "reason_codes": []}
    assert candidate["prompt"]["utf8_bytes"] > 0


def test_a2_candidate_restores_full_layout_structure_and_tail_meaning() -> None:
    report = a2.measure()
    layout = report["layout"]
    candidate = layout["a2_lower_bound_candidate"]

    assert layout["production_caps_restored"] is True
    assert candidate["projected_cards"] == 300
    assert candidate["relative_coordinates"] == 300
    assert candidate["relations"] == 300
    assert candidate["complete_island_memberships"] == 30
    assert candidate["tail_coordinates_present"] == ["c298", "c299"]
    assert candidate["tail_required_relations_present"] == [
        ("c298", "c299", "causal"),
        ("c299", "c000", "negate"),
    ]
    assert candidate["truncation"] == {"truncated": False, "reason_codes": []}
    assert candidate["prompt"]["utf8_bytes"] > 0


def test_temporary_budget_restores_constants_even_when_body_raises() -> None:
    doc = _late_layout_document()
    before = (ir_module.MAX_CARDS, ir_module.MAX_TEXT_CHARS, ir_module.MAX_RELATIONS)

    with pytest.raises(RuntimeError, match="fixture failure"):
        with a2._temporary_representative_fit_budget(doc):
            assert ir_module.MAX_CARDS == 300
            assert ir_module.MAX_TEXT_CHARS == 13_800
            raise RuntimeError("fixture failure")

    assert (ir_module.MAX_CARDS, ir_module.MAX_TEXT_CHARS, ir_module.MAX_RELATIONS) == before


def test_measurement_does_not_claim_tokens_or_change_production_caps() -> None:
    before = (ir_module.MAX_CARDS, ir_module.MAX_TEXT_CHARS, ir_module.MAX_RELATIONS)
    report = a2.measure()
    after = (ir_module.MAX_CARDS, ir_module.MAX_TEXT_CHARS, ir_module.MAX_RELATIONS)

    assert before == after == (200, 12_000, 400)
    assert "lower-bound fixture" in report["interpretation_boundary"]
    assert "not token counts" in report["interpretation_boundary"]
    assert "No provider is called" in report["interpretation_boundary"]


def test_documented_direct_cli_runs_without_network_access() -> None:
    backend_dir = Path(__file__).resolve().parents[1]
    completed = subprocess.run(
        [sys.executable, "scripts/measure_ai_route_a2_candidate.py"],
        cwd=backend_dir,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)

    assert report["measurement"] == "ai-route-a2-lower-bound-candidate-at-scale"
    assert report["groups"]["a2_lower_bound_candidate"]["projected_cards"] == 300
    assert report["layout"]["a2_lower_bound_candidate"]["relative_coordinates"] == 300
    assert report["groups"]["production_caps_restored"] is True
    assert report["layout"]["production_caps_restored"] is True
