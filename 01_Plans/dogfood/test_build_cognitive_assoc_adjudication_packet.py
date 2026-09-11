#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from build_cognitive_assoc_adjudication_packet import (
    build_packet,
    load_model_input,
    validate_contrast_pool,
)


class CognitiveAssocAdjudicationPacketTest(unittest.TestCase):
    def cards(self) -> dict[tuple[str, str], str]:
        return {
            ("doc", "c1"): "表層語彙が違っても同じ訴えを持つことがある。",
            ("doc", "c2"): "一緒に読むことで共通構造が立ち上がる。",
            ("doc", "c3"): "似た言葉でも別の訴えなら分ける。",
        }

    def pool(self) -> dict[str, object]:
        labels = [
            "hard_negative",
            "related_but_separate",
            "ambiguous_or_held",
            "exclude",
        ]
        return {
            "benchmarkId": "fixture-v0",
            "status": "pending_human",
            "semanticBaselineGate": "closed",
            "modelOutputsAllowed": False,
            "pairCandidates": [
                {
                    "id": "doc:pair:c1+c3",
                    "documentId": "doc",
                    "cardIds": ["c1", "c3"],
                    "label": "pending_human",
                    "allowedLabels": labels,
                }
            ],
            "twoPlusOneCandidates": [
                {
                    "id": "doc:2plus1:g1:c1+c2+c3",
                    "documentId": "doc",
                    "cardIds": ["c1", "c2", "c3"],
                    "label": "pending_human",
                    "allowedLabels": labels,
                }
            ],
        }

    def test_packet_contains_cards_and_no_model_score_fields(self) -> None:
        packet = build_packet(self.pool(), self.cards())

        self.assertIn("表層語彙が違っても同じ訴え", packet)
        self.assertIn("semantic baseline gate CLOSED", packet)
        self.assertIn("`PENDING`", packet)
        self.assertNotIn("similarity", packet.lower())
        self.assertNotIn("confidence", packet.lower())
        self.assertNotIn("島名", packet.split("---", 1)[-1])

    def test_open_semantic_gate_is_rejected(self) -> None:
        pool = self.pool()
        pool["semanticBaselineGate"] = "open"
        with self.assertRaisesRegex(ValueError, "must remain closed"):
            validate_contrast_pool(pool)

    def test_prelabelled_candidate_is_rejected(self) -> None:
        pool = self.pool()
        pool["pairCandidates"][0]["label"] = "hard_negative"
        with self.assertRaisesRegex(ValueError, "already labelled"):
            validate_contrast_pool(pool)

    def test_source_island_leak_is_rejected(self) -> None:
        pool = self.pool()
        pool["pairCandidates"][0]["sourceIslandId"] = "i1"
        with self.assertRaisesRegex(ValueError, "leaks forbidden fields"):
            validate_contrast_pool(pool)

    def test_model_output_leak_is_rejected(self) -> None:
        pool = self.pool()
        pool["pairCandidates"][0]["modelOutput"] = "この二枚は近い"
        with self.assertRaisesRegex(ValueError, "leaks forbidden fields"):
            validate_contrast_pool(pool)

    def test_model_input_must_contain_only_blind_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "model-input.jsonl"
            path.write_text(
                json.dumps(
                    {
                        "documentId": "doc",
                        "cardId": "c1",
                        "text": "本文",
                        "islandId": "i1",
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "unexpected fields"):
                load_model_input(path)


if __name__ == "__main__":
    unittest.main()
