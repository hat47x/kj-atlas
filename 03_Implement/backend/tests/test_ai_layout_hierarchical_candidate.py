from __future__ import annotations

import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest

from scripts import measure_ai_layout_hierarchical_candidate as layout_c
from scripts.measure_ai_route_projection_candidates import _late_layout_document


def test_hierarchical_candidate_preserves_all_cards_relations_and_islands() -> None:
    report = layout_c.measure()
    candidate = report["hierarchical_c_candidate"]
    coverage = candidate["coverage"]

    assert report["source"] == {"cards": 300, "islands": 30, "relations": 300}
    assert candidate["requests"] == 31
    assert candidate["local_batches"] == 30
    assert candidate["max_cards_per_local_batch"] == 10

    assert coverage["source_cards"] == 300
    assert coverage["assigned_cards"] == 300
    assert coverage["unique_assigned_cards"] == 300
    assert coverage["source_relations"] == 300
    assert coverage["local_relations"] == 270
    assert coverage["global_relations"] == 30
    assert coverage["unique_relation_ids"] == 300
    assert coverage["source_islands"] == 30
    assert coverage["island_batches"] == 30
    assert coverage["lone_card_batches"] == 0

    tail = candidate["tail_checks"]
    assert tail["c298_c299_same_local_batch"] is True
    assert "e298" in tail["tail_local_relation_ids"]
    assert tail["c299_c000_cross_bridge_count"] == 1
    assert tail["c299_c000_cross_bridge_types"] == ["negate"]


def test_hierarchical_candidate_reduces_largest_single_request_without_claiming_tokens() -> None:
    report = layout_c.measure()
    route_b_bytes = report["route_b_one_shot"]["prompt"]["utf8_bytes"]
    prompt_bytes = report["hierarchical_c_candidate"]["prompt_bytes"]

    assert route_b_bytes == 128_562
    assert prompt_bytes["max_single_request"] < route_b_bytes
    assert prompt_bytes["min_local_request"] > 0
    assert prompt_bytes["max_local_request"] > 0
    assert prompt_bytes["global_alignment_request"] > 0
    assert prompt_bytes["aggregate_all_requests"] >= prompt_bytes["max_single_request"]
    assert "not token counts" in report["interpretation_boundary"]


def test_partition_is_deterministic_under_source_order_reversal() -> None:
    doc = _late_layout_document()
    reversed_doc = deepcopy(doc)
    reversed_doc["cards"] = list(reversed(reversed_doc["cards"]))
    reversed_doc["islands"] = list(reversed(reversed_doc["islands"]))
    reversed_doc["edges"] = list(reversed(reversed_doc["edges"]))

    first = layout_c.build_hierarchical_layout_candidate(doc)
    second = layout_c.build_hierarchical_layout_candidate(reversed_doc)

    assert first["batches"] == second["batches"]
    assert first["coverage"] == second["coverage"]
    assert [
        (item["batch_id"], item["card_ids"], item["relation_ids"], item["prompt"])
        for item in first["local_prompts"]
    ] == [
        (item["batch_id"], item["card_ids"], item["relation_ids"], item["prompt"])
        for item in second["local_prompts"]
    ]
    assert first["global_relations"] == second["global_relations"]
    assert first["global_prompt"] == second["global_prompt"]


def test_multiple_direct_membership_fails_closed() -> None:
    doc = _late_layout_document()
    doc["islands"][1]["cardIds"].append("c000")

    with pytest.raises(ValueError, match="multiple direct island batches"):
        layout_c.build_hierarchical_layout_candidate(doc)


def test_lone_card_becomes_singleton_batch_instead_of_disappearing() -> None:
    doc = _late_layout_document()
    doc["islands"][0]["cardIds"].remove("c000")

    plan = layout_c.build_hierarchical_layout_candidate(doc)
    lone = next(batch for batch in plan["batches"] if batch["batch_id"] == "lone:c000")

    assert lone["kind"] == "lone_card"
    assert lone["card_ids"] == ["c000"]
    assert plan["coverage"]["assigned_cards"] == 300
    assert plan["coverage"]["unique_assigned_cards"] == 300
    # e000 crosses from the singleton to island i00, and e299 crosses back to it.
    bridges = {
        (row.get("from_id"), row.get("to_id"), row.get("type"))
        for row in plan["global_relations"]
    }
    assert ("c000", "c001", "related") in bridges
    assert ("c299", "c000", "negate") in bridges


def test_documented_direct_cli_runs_without_network_access() -> None:
    backend_dir = Path(__file__).resolve().parents[1]
    completed = subprocess.run(
        [sys.executable, "scripts/measure_ai_layout_hierarchical_candidate.py"],
        cwd=backend_dir,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)

    assert report["measurement"] == "ai-layout-hierarchical-candidate-at-scale"
    assert report["hierarchical_c_candidate"]["requests"] == 31
    assert report["hierarchical_c_candidate"]["coverage"]["unique_relation_ids"] == 300
