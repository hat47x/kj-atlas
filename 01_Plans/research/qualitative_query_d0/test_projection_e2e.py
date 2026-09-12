from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from execute_projection_request import D0ExecutionError, execute_projection_request  # noqa: E402

NETWORK_PATH = ROOT / "fixtures" / "network.json"
REQUESTS_PATH = ROOT / "fixtures" / "projection_requests.json"
FORBIDDEN_RANKING_KEYS = {"score", "confidence", "importance", "rank"}


class D0ProjectionE2ETests(unittest.TestCase):
    def setUp(self) -> None:
        self.network = json.loads(NETWORK_PATH.read_text(encoding="utf-8"))
        self.requests = json.loads(REQUESTS_PATH.read_text(encoding="utf-8"))

    def assert_no_ranking_keys(self, value) -> None:
        if isinstance(value, dict):
            self.assertTrue(FORBIDDEN_RANKING_KEYS.isdisjoint(value.keys()), value)
            for child in value.values():
                self.assert_no_ranking_keys(child)
        elif isinstance(value, list):
            for child in value:
                self.assert_no_ranking_keys(child)

    def test_human_ai_sei_share_selection_but_receive_different_projection_forms(self) -> None:
        results = [
            execute_projection_request(self.network, request)
            for request in self.requests["sameContrast"]
        ]
        self.assertEqual(len({result["selectionDigest"] for result in results}), 1)
        self.assertEqual(
            [result["selection"]["selectedNodeRefs"] for result in results],
            [["c1", "c5"], ["c1", "c5"], ["c1", "c5"]],
        )

        human_forms = [item["projectionForm"] for item in results[0]["projections"]]
        ai_forms = [item["projectionForm"] for item in results[1]["projections"]]
        sei_forms = [item["projectionForm"] for item in results[2]["projections"]]
        self.assertEqual(human_forms, ["comparison_table", "spatial_layout"])
        self.assertEqual(ai_forms, ["comparison_table"])
        self.assertEqual(sei_forms, ["subgraph"])

    def test_actor_identity_is_trace_not_selection_input(self) -> None:
        human = execute_projection_request(self.network, self.requests["sameContrast"][0])
        sei = execute_projection_request(self.network, self.requests["sameContrast"][2])
        self.assertNotEqual(human["actor"]["actorRef"], sei["actor"]["actorRef"])
        self.assertEqual(human["selectionDigest"], sei["selectionDigest"])
        rendered_selection = json.dumps(human["selection"], ensure_ascii=False)
        self.assertNotIn(human["actor"]["actorRef"], rendered_selection)
        self.assertNotIn(sei["actor"]["actorRef"], rendered_selection)

    def test_ai_narrative_is_deferred_to_d4_not_generated_in_d0(self) -> None:
        request = self.requests["sameContrast"][1]
        result = execute_projection_request(self.network, request)
        self.assertEqual(
            result["deferredProjectionForms"],
            [
                {
                    "form": "compact_narrative",
                    "tier": "D4",
                    "reason": "generated narrative is outside deterministic D0",
                }
            ],
        )

    def test_unreviewed_focus_is_hidden_without_safe_mode_allowance(self) -> None:
        request = self.requests["unreviewedNeighborhood"]
        with self.assertRaises(D0ExecutionError):
            execute_projection_request(
                self.network,
                request,
                safe_mode_allows_unreviewed=False,
            )

    def test_unreviewed_focus_requires_permission_and_safe_mode(self) -> None:
        request = self.requests["unreviewedNeighborhood"]
        allowed = execute_projection_request(
            self.network,
            request,
            safe_mode_allows_unreviewed=True,
        )
        self.assertEqual(allowed["trace"]["reviewVisibility"], "include_unreviewed")
        self.assertEqual(allowed["selection"]["selectedNodeRefs"], ["c7", "c8"])

        denied_request = copy.deepcopy(request)
        denied_request["permission"]["canSeeUnreviewed"] = False
        with self.assertRaises(D0ExecutionError):
            execute_projection_request(
                self.network,
                denied_request,
                safe_mode_allows_unreviewed=True,
            )

    def test_query_and_projection_do_not_mutate_original_network(self) -> None:
        before = copy.deepcopy(self.network)
        for request in self.requests["sameContrast"]:
            execute_projection_request(self.network, request)
        self.assertEqual(self.network, before)

    def test_response_has_no_ranking_semantics(self) -> None:
        result = execute_projection_request(self.network, self.requests["sameContrast"][0])
        self.assert_no_ranking_keys(result)

    def test_multiple_d0_selection_intents_fail_closed(self) -> None:
        request = copy.deepcopy(self.requests["sameContrast"][0])
        request["interest"]["seek"] = ["contrast", "provenance"]
        with self.assertRaisesRegex(D0ExecutionError, "exactly one"):
            execute_projection_request(self.network, request)

    def test_affinity_is_deferred_not_silently_treated_as_d0(self) -> None:
        request = copy.deepcopy(self.requests["sameContrast"][2])
        request["interest"]["seek"] = ["affinity"]
        with self.assertRaisesRegex(D0ExecutionError, "exactly one"):
            execute_projection_request(self.network, request)

    def test_legacy_request_key_is_rejected(self) -> None:
        request = copy.deepcopy(self.requests["sameContrast"][0])
        request["previewConfirmed"] = True
        with self.assertRaisesRegex(D0ExecutionError, "unknown keys"):
            execute_projection_request(self.network, request)


if __name__ == "__main__":
    unittest.main()
