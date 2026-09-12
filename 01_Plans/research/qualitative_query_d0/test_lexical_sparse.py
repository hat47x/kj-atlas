from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lexical_sparse import (  # noqa: E402
    D1LexicalError,
    character_ngrams,
    lexical_expand,
    lexical_expand_from_snapshot,
)
from query_engine import D0Network  # noqa: E402

NETWORK_PATH = ROOT / "fixtures" / "network.json"
FORBIDDEN_RANKING_KEYS = {"score", "confidence", "importance", "rank"}


class D1LexicalSparseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.snapshot = json.loads(NETWORK_PATH.read_text(encoding="utf-8"))
        self.network = D0Network(self.snapshot)

    def assert_no_ranking_keys(self, value) -> None:
        if isinstance(value, dict):
            self.assertTrue(FORBIDDEN_RANKING_KEYS.isdisjoint(value.keys()), value)
            for child in value.values():
                self.assert_no_ranking_keys(child)
        elif isinstance(value, list):
            for child in value:
                self.assert_no_ranking_keys(child)

    def test_nfkc_and_casefold_are_surface_normalization_only(self) -> None:
        self.assertEqual(
            character_ngrams("ＡＢ-c"),
            character_ngrams("abＣ"),
        )

    def test_anchor_is_not_returned_as_candidate(self) -> None:
        result = lexical_expand(self.network, ["c1"])
        self.assertNotIn("c1", result["candidateRefs"])

    def test_candidates_are_ordered_by_ref_not_overlap_strength(self) -> None:
        result = lexical_expand(self.network, ["c1"])
        self.assertEqual(result["candidateRefs"], sorted(result["candidateRefs"]))
        self.assertIn("c3", result["candidateRefs"])
        self.assertIn("c8", result["candidateRefs"])
        self.assertLess(result["candidateRefs"].index("c3"), result["candidateRefs"].index("c8"))

    def test_evidence_is_shared_surface_ngrams_not_similarity_score(self) -> None:
        result = lexical_expand(self.network, ["c1"])
        c2 = next(item for item in result["items"] if item["ref"] == "c2")
        grams = c2["evidence"]["sharedCharacterNgrams"]
        self.assertIn("確認", grams)
        self.assertIn("作業", grams)
        self.assert_no_ranking_keys(result)
        self.assertFalse(result["trace"]["semanticInference"])

    def test_lexically_distant_text_is_not_invented_as_semantic_match(self) -> None:
        snapshot = copy.deepcopy(self.snapshot)
        snapshot["nodes"].append(
            {
                "id": "semantic-only",
                "kind": "card",
                "text": "完全に異なる語彙で同じ意味を表す仮想例",
                "reviewState": "human_reviewed",
                "sourceRefs": [],
                "actorRefs": [],
            }
        )
        result = lexical_expand_from_snapshot(snapshot, ["c1"])
        self.assertNotIn("semantic-only", result["candidateRefs"])

    def test_scope_bounds_candidate_generation(self) -> None:
        result = lexical_expand(self.network, ["c1"], scope_refs=["c1", "c2", "c8"])
        self.assertEqual(result["candidateRefs"], ["c2", "c8"])

    def test_multiple_anchors_preserve_which_anchor_matched(self) -> None:
        result = lexical_expand(self.network, ["c1", "c5"], min_shared_features=1)
        c7 = next(item for item in result["items"] if item["ref"] == "c7")
        self.assertTrue(set(c7["matchedAnchorRefs"]).issubset({"c1", "c5"}))
        self.assertTrue(c7["matchedAnchorRefs"])

    def test_no_text_node_is_ignored_without_failure(self) -> None:
        snapshot = copy.deepcopy(self.snapshot)
        snapshot["nodes"].append(
            {
                "id": "concept-no-text",
                "kind": "concept",
                "reviewState": "human_reviewed",
                "sourceRefs": [],
                "actorRefs": [],
            }
        )
        result = lexical_expand_from_snapshot(snapshot, ["c1"])
        self.assertNotIn("concept-no-text", result["candidateRefs"])

    def test_unknown_anchor_fails_closed(self) -> None:
        with self.assertRaisesRegex(D1LexicalError, "unknown refs"):
            lexical_expand(self.network, ["missing"])

    def test_invalid_threshold_fails_closed(self) -> None:
        with self.assertRaisesRegex(D1LexicalError, "positive integer"):
            lexical_expand(self.network, ["c1"], min_shared_features=0)

    def test_query_does_not_mutate_snapshot(self) -> None:
        before = copy.deepcopy(self.snapshot)
        lexical_expand_from_snapshot(self.snapshot, ["c1"])
        self.assertEqual(self.snapshot, before)


if __name__ == "__main__":
    unittest.main()
