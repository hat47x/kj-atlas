#!/usr/bin/env python3
from __future__ import annotations

import unittest

from select_cognitive_assoc_adjudication_set import (
    jaccard,
    select_collection,
)


LABELS = [
    "hard_negative",
    "related_but_separate",
    "ambiguous_or_held",
    "exclude",
]


class CognitiveAssocAdjudicationSelectionTest(unittest.TestCase):
    def candidate(self, suffix: str, ids: list[str]) -> dict[str, object]:
        kind = "pair" if len(ids) == 2 else "2plus1"
        return {
            "id": f"doc:{kind}:{suffix}",
            "documentId": "doc",
            "cardIds": ids,
            "label": "pending_human",
            "allowedLabels": LABELS,
        }

    def test_jaccard_uses_nfkc_and_ignores_punctuation(self) -> None:
        left = "ＡＩ・提案を、人間が確認する。"
        right = "AI提案を人間が確認する"
        self.assertEqual(1.0, jaccard(left, right))

    def test_pair_lexical_stress_prefers_surface_overlap(self) -> None:
        cards = {
            ("doc", "a"): "文書更新が人間の記憶と善意に依存する",
            ("doc", "b"): "文書更新を人間の善意だけに依存させない",
            ("doc", "c"): "全く別の語彙で別件を述べる",
        }
        candidates = [
            self.candidate("a+b", ["a", "b"]),
            self.candidate("a+c", ["a", "c"]),
        ]
        selected = select_collection(candidates, cards, uniform_n=0, lexical_n=1)
        self.assertEqual("doc:pair:a+b", selected[0]["id"])
        self.assertEqual(["L"], selected[0]["selectionStrata"])

    def test_two_plus_one_scores_outsider_against_each_group_member(self) -> None:
        cards = {
            ("doc", "a"): "警告を構造的情報として扱う",
            ("doc", "b"): "空白を構造的情報として扱う",
            ("doc", "x"): "警告を単なる問題として扱う",
            ("doc", "y"): "外部利用者の価値を検証する",
        }
        candidates = [
            self.candidate("a+b+x", ["a", "b", "x"]),
            self.candidate("a+b+y", ["a", "b", "y"]),
        ]
        selected = select_collection(candidates, cards, uniform_n=0, lexical_n=1)
        self.assertEqual("doc:2plus1:a+b+x", selected[0]["id"])

    def test_overlap_between_u_and_l_is_deduplicated_and_records_both(self) -> None:
        cards = {
            ("doc", "a"): "同じ文章の一部を共有する候補",
            ("doc", "b"): "同じ文章の一部を共有する候補です",
        }
        candidate = self.candidate("a+b", ["a", "b"])
        selected = select_collection([candidate], cards, uniform_n=1, lexical_n=1)
        self.assertEqual(1, len(selected))
        self.assertEqual(["U", "L"], selected[0]["selectionStrata"])

    def test_selection_order_is_candidate_id_not_score_order(self) -> None:
        cards = {
            ("doc", "a"): "かなり似た文章です",
            ("doc", "b"): "かなり似た文章です",
            ("doc", "c"): "別内容",
        }
        candidates = [
            self.candidate("z", ["a", "b"]),
            self.candidate("a", ["a", "c"]),
        ]
        selected = select_collection(candidates, cards, uniform_n=0, lexical_n=2)
        self.assertEqual(["doc:pair:a", "doc:pair:z"], [item["id"] for item in selected])


if __name__ == "__main__":
    unittest.main()
