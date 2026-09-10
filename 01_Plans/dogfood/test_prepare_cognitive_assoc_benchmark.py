#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from prepare_cognitive_assoc_benchmark import (
    ALLOWED_MODEL_FIELDS,
    derive_pair_pool,
    git_blob_sha,
    prepare,
    prepare_source,
)


class CognitiveAssocBenchmarkPreparationTest(unittest.TestCase):
    def write_json(self, root: Path, relative: str, payload: object) -> Path:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        return path

    def source_spec(self, source_path: Path, root: Path) -> dict[str, object]:
        raw = source_path.read_bytes()
        return {
            "documentId": "doc_fixture",
            "path": str(source_path.relative_to(root)),
            "blobSha": git_blob_sha(raw),
            "reviewedCardCount": 4,
            "observedPositiveSets": [
                {"sourceIslandId": "i1", "cardIds": ["c1", "c2"]}
            ],
            "observedSingletonIslands": [
                {"sourceIslandId": "i2", "cardId": "c3"},
                {"sourceIslandId": "i3", "cardId": "c4"},
            ],
            "challengePositiveSets": [["c1", "c2"]],
        }

    def manifest(self, source_spec: dict[str, object]) -> dict[str, object]:
        return {
            "id": "fixture-v0",
            "status": "pre_adjudication_frozen",
            "inputContract": {
                "modelVisibleFields": ["documentId", "cardId", "text"],
                "eligibility": (
                    "Only cards with textReviewed=true may enter model evaluation "
                    "in benchmark v0."
                ),
                "noModelRunBeforeAdjudication": True,
            },
            "sources": [source_spec],
        }

    def reviewed_document(self) -> dict[str, object]:
        return {
            "id": "doc_fixture",
            "cards": [
                {
                    "id": "c1",
                    "x": 1,
                    "y": 2,
                    "text": "異なる具体例の背後に同じ訴えがある。",
                    "textReviewed": True,
                    "meta": {"source": "secret-source-a"},
                },
                {
                    "id": "c2",
                    "x": 3,
                    "y": 4,
                    "text": "表層語彙が違っても同じ問題構造を扱う。",
                    "textReviewed": True,
                    "meta": {"source": "secret-source-b"},
                },
                {
                    "id": "c3",
                    "x": 5,
                    "y": 6,
                    "text": "似た単語でも訴えが違えば分ける。",
                    "textReviewed": True,
                    "meta": {"source": "secret-source-c"},
                },
                {
                    "id": "c4",
                    "x": 7,
                    "y": 8,
                    "text": "一枚だけで島として成立することもある。",
                    "textReviewed": True,
                    "meta": {"source": "secret-source-d"},
                },
            ],
            "islands": [
                {"id": "i1", "title": "モデルへ見せない表札", "cardIds": ["c1", "c2"]},
                {"id": "i2", "title": "別の単独島", "cardIds": ["c3"]},
                {"id": "i3", "title": "単独", "cardIds": ["c4"]},
            ],
            "edges": [{"id": "e1", "fromId": "c1", "toId": "c3", "type": "related"}],
        }

    def test_prepare_emits_only_blind_card_fields_and_keeps_gate_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_path = self.write_json(root, "source.json", self.reviewed_document())
            spec = self.source_spec(source_path, root)
            manifest_path = self.write_json(root, "manifest.json", self.manifest(spec))

            model_input, adjudication = prepare(manifest_path, root)

            self.assertEqual(4, len(model_input))
            for card in model_input:
                self.assertEqual(ALLOWED_MODEL_FIELDS, tuple(card.keys()))
                self.assertNotIn("x", card)
                self.assertNotIn("meta", card)
                self.assertNotIn("islandId", card)
            self.assertEqual("closed", adjudication["semanticBaselineGate"])
            self.assertFalse(adjudication["modelOutputsAllowed"])

    def test_unreviewed_eligible_card_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            document = self.reviewed_document()
            document["cards"][2]["textReviewed"] = False
            source_path = self.write_json(root, "source.json", document)
            spec = self.source_spec(source_path, root)

            with self.assertRaisesRegex(ValueError, "unreviewed card"):
                prepare_source(root, spec)

    def test_blob_sha_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_path = self.write_json(root, "source.json", self.reviewed_document())
            spec = self.source_spec(source_path, root)
            spec["blobSha"] = "0" * 40

            with self.assertRaisesRegex(ValueError, "source blob mismatch"):
                prepare_source(root, spec)

    def test_pair_pool_excludes_co_island_but_keeps_distinct_singletons(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_path = self.write_json(root, "source.json", self.reviewed_document())
            source = prepare_source(root, self.source_spec(source_path, root))

            pairs = {tuple(item["cardIds"]) for item in derive_pair_pool(source)}

            self.assertNotIn(("c1", "c2"), pairs)
            self.assertIn(("c1", "c3"), pairs)
            self.assertIn(("c1", "c4"), pairs)
            self.assertIn(("c3", "c4"), pairs)

    def test_challenge_set_may_not_cross_observed_islands(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_path = self.write_json(root, "source.json", self.reviewed_document())
            spec = self.source_spec(source_path, root)
            spec["challengePositiveSets"] = [["c1", "c3"]]

            with self.assertRaisesRegex(ValueError, "challengePositiveSet crosses"):
                prepare_source(root, spec)

    def test_every_eligible_card_requires_observed_island_membership(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_path = self.write_json(root, "source.json", self.reviewed_document())
            spec = self.source_spec(source_path, root)
            spec["observedSingletonIslands"] = [
                {"sourceIslandId": "i2", "cardId": "c3"}
            ]

            with self.assertRaisesRegex(ValueError, "lack observed island membership"):
                prepare_source(root, spec)


if __name__ == "__main__":
    unittest.main()
