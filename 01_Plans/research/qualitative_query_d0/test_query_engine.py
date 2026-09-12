from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from projection import D0ProjectionError, project  # noqa: E402
from query_engine import D0Network, D0QueryError  # noqa: E402

FIXTURE = ROOT / "fixtures" / "network.json"
FORBIDDEN_RANKING_KEYS = {"score", "confidence", "importance", "rank"}


class D0QualitativeQueryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.network = D0Network(self.raw)

    def assert_no_ranking_keys(self, value) -> None:
        if isinstance(value, dict):
            self.assertTrue(FORBIDDEN_RANKING_KEYS.isdisjoint(value.keys()), value)
            for child in value.values():
                self.assert_no_ranking_keys(child)
        elif isinstance(value, list):
            for child in value:
                self.assert_no_ranking_keys(child)

    def test_neighborhood_is_explicit_graph_bfs(self) -> None:
        depth1 = self.network.neighborhood(["c1"], depth=1)
        self.assertEqual(depth1["selectedNodeRefs"], ["c1", "c2"])
        self.assertEqual(depth1["distanceByRef"], {"c1": 0, "c2": 1})

        depth2 = self.network.neighborhood(["c1"], depth=2)
        self.assertEqual(depth2["selectedNodeRefs"], ["c1", "c2", "c3", "c4"])
        self.assertEqual(depth2["distanceByRef"]["c3"], 2)
        self.assertEqual(depth2["distanceByRef"]["c4"], 2)

    def test_contrast_keeps_shared_and_separate_facets(self) -> None:
        result = self.network.contrast(["c1", "c2"], ["c3", "c4"])
        self.assertEqual(result["facets"]["sources"]["shared"], ["s2"])
        self.assertEqual(result["facets"]["sources"]["leftOnly"], ["s1"])
        self.assertEqual(result["facets"]["sources"]["rightOnly"], ["s3"])
        self.assertEqual(result["facets"]["islands"]["leftOnly"], ["i1"])
        self.assertEqual(result["facets"]["islands"]["rightOnly"], ["i2"])
        self.assertEqual(result["facets"]["holdStates"]["rightOnly"], ["held"])

    def test_bridge_returns_multiple_shortest_paths_without_strength_score(self) -> None:
        result = self.network.bridge("c1", "c5")
        self.assertEqual(
            result["nodePaths"],
            [["c1", "c2", "c3", "c5"], ["c1", "c2", "c4", "c5"]],
        )
        self.assertEqual(result["status"], "explicit_paths_found")
        self.assert_no_ranking_keys(result)

    def test_no_explicit_bridge_is_not_reported_as_unrelated(self) -> None:
        result = self.network.bridge("c1", "c7")
        self.assertEqual(result["status"], "no_explicit_path")
        self.assertEqual(result["nodePaths"], [])
        self.assertNotIn("unrelated", json.dumps(result))

    def test_residual_returns_parallel_reasons_not_score(self) -> None:
        result = self.network.residual()
        by_ref = {item["ref"]: item["reasons"] for item in result["items"]}
        self.assertIn("singleton_island", by_ref["c5"])
        self.assertIn("held_or_pending", by_ref["c4"])
        self.assertIn("has_critique", by_ref["c4"])
        self.assertEqual(
            by_ref["c6"],
            ["held_or_pending", "missing_provenance", "unconnected"],
        )
        self.assertIn("unresolved_contradiction", by_ref["c7"])
        self.assertIn("unresolved_contradiction", by_ref["c8"])
        self.assert_no_ranking_keys(result)

    def test_unresolved_preserves_hold_review_critique_and_contradiction(self) -> None:
        result = self.network.unresolved()
        by_ref = {item["ref"]: item for item in result["items"]}
        self.assertIn("hold:held", by_ref["c4"]["reasons"])
        self.assertIn("critique:open", by_ref["c4"]["reasons"])
        self.assertIn("hold:pending", by_ref["c6"]["reasons"])
        self.assertIn("review:unreviewed", by_ref["c7"]["reasons"])
        self.assertEqual(result["contradictionRefs"], ["x1"])
        self.assertIn("c8", result["selectedNodeRefs"])

    def test_temporal_is_ordering_not_causality(self) -> None:
        result = self.network.temporal()
        timestamps = [item["at"] for item in result["records"]]
        self.assertEqual(timestamps, sorted(timestamps))
        self.assertEqual(result["trace"]["method"], "explicit_timestamp_order")
        self.assertNotIn("causal", json.dumps(result))

    def test_provenance_groups_sources_and_actors_and_keeps_missing(self) -> None:
        result = self.network.provenance()
        self.assertEqual(result["bySource"]["s1"], ["c1", "c2"])
        self.assertEqual(result["byActor"]["ai:1"], ["c4", "c7"])
        self.assertEqual(result["missingSourceRefs"], ["c6"])

    def test_same_selection_can_be_projected_differently(self) -> None:
        result = self.network.contrast(["c1", "c2"], ["c3", "c4"])
        table = project(self.network, result, "comparison_table")
        subgraph = project(self.network, result, "subgraph")
        layout = project(self.network, result, "spatial_layout")
        self.assertEqual(table["selectedNodeRefs"], subgraph["selectedNodeRefs"])
        self.assertEqual(table["selectedNodeRefs"], layout["selectedNodeRefs"])
        self.assertEqual(table["selectionTrace"], subgraph["selectionTrace"])
        self.assertEqual(table["selectionTrace"], layout["selectionTrace"])

    def test_d0_refuses_generated_narrative_projection(self) -> None:
        result = self.network.neighborhood(["c1"], depth=1)
        with self.assertRaisesRegex(D0ProjectionError, "belongs to D4"):
            project(self.network, result, "compact_narrative")

    def test_query_does_not_mutate_source_network(self) -> None:
        before = copy.deepcopy(self.raw)
        self.network.neighborhood(["c1"], depth=3)
        self.network.contrast(["c1"], ["c5"])
        self.network.bridge("c1", "c5")
        self.network.residual()
        self.network.unresolved()
        self.network.temporal()
        self.network.provenance()
        self.assertEqual(self.network.snapshot(), before)
        self.assertEqual(self.raw, before)

    def test_unknown_refs_fail_closed(self) -> None:
        with self.assertRaises(D0QueryError):
            self.network.neighborhood(["missing"], depth=1)
        with self.assertRaises(D0QueryError):
            self.network.bridge("c1", "missing")


if __name__ == "__main__":
    unittest.main()
