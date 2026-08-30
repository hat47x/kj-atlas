#!/usr/bin/env python3
"""Contract tests for cognitive dogfood static intake validation.

These tests contain no experiment result. They only verify that the intake gate
accepts structurally complete records and rejects comparison-breaking omissions.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import validate_cognitive_run_records as validator


def build_case001_arm_c_record(
    *,
    artifact_name: str = "cognitive-dogfood-case-001-arm-c",
    artifact_head: str = "a" * 40,
    artifact_digest: str = "sha256:" + "b" * 64,
    contamination: str = "none",
    required_numbers: list[int] | None = None,
) -> str:
    if required_numbers is None:
        required_numbers = list(range(1, 10))

    required_output = "\n\n".join(
        f"### 6.{number} Required item {number}\n\nResult: substantive result {number}."
        for number in required_numbers
    )

    question = validator.CASE_CONTRACTS["case-001"]["question"]
    product_sha = validator.PRODUCT_SHA

    return f"""# Synthetic intake record

## 0. Run metadata

- Case ID: case-001
- Round: 1
- Arm: C
- Blind alias: cedar-17
- Run ID: case001-c-run001
- Run validity: valid
- Date: 2026-08-30
- Execution order position: 1/4
- Operator: operator-test
- Model/provider: synthetic/provider
- KJ Atlas version/commit: {product_sha}
- cultural-substrate-weaving version/commit: N/A
- Source manifest ID: case-001-r1-product@{product_sha}
- Execution artifact name: {artifact_name}
- Execution artifact workflow head: {artifact_head}
- Execution artifact digest: {artifact_digest}
- Operator pack/version: frozen-case001
- Context started fresh: yes
- Known contamination: {contamination}
- Operator/setup friction log: none

## 1. Fixed question

{question}

## 2. Input verification

All fixed inputs verified.

## 3. Pre-analysis state

No result known in advance.

## 4. Raw analysis artifacts

- KJ Atlas document ID/file: synthetic-canvas.json
- InquiryJourney/bundle reference: synthetic-inquiry.json
- Raw card count: 1

## 5. AI proposal ledger

none used

## 6. Required output

{required_output}

## 7. Conflict-bearing source check

- T1 detected: yes
- T2 detected: partial
- T3 detected: no

## 8. M1–M9 evidence

### M1 生存所見

recorded

### M2 根拠接地

recorded

### M3 異論・残差保持

recorded

### M4 早期収束耐性

recorded

### M5 AI依存校正

recorded

### M6 再訪・訂正可能性

recorded

### M7 注意・探索制御

recorded

### M8 決定への変換品質

recorded

### M9 認知摩擦

recorded

## 9. Retention audit

complete

## 10. InquiryJourney actual-use record (C/D only)

- InquiryJourney ID / bundle reference: synthetic-inquiry.json
- Working document ID/file: synthetic-canvas.json

## 11. Candidate source requests

none

## 13. Static intake validation

pending synthetic validation
"""


class RequiredOutputNumberingTests(unittest.TestCase):
    def test_complete_sequence_passes(self) -> None:
        text = "\n".join(
            f"### 6.{number} Item {number}\nbody"
            for number in range(1, 10)
        )
        self.assertEqual(validator.validate_required_output_numbering(text, 9), [])

    def test_missing_item_fails(self) -> None:
        text = "\n".join(
            f"### 6.{number} Item {number}\nbody"
            for number in (1, 2, 4, 5, 6, 7, 8, 9)
        )
        errors = validator.validate_required_output_numbering(text, 9)
        self.assertTrue(any("missing=[3]" in error for error in errors), errors)

    def test_duplicate_item_fails(self) -> None:
        text = "\n".join(
            f"### 6.{number} Item {number}\nbody"
            for number in (1, 2, 3, 3, 4, 5, 6, 7, 8, 9)
        )
        errors = validator.validate_required_output_numbering(text, 9)
        self.assertTrue(any("duplicates=[3]" in error for error in errors), errors)


class FullRecordTests(unittest.TestCase):
    def validate_text(self, text: str) -> tuple[list[str], list[str]]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cedar-17-record.md"
            path.write_text(text, encoding="utf-8")
            return validator.validate_record(path)

    def test_valid_case001_arm_c_record_passes(self) -> None:
        errors, warnings = self.validate_text(build_case001_arm_c_record())
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_incomplete_required_output_fails(self) -> None:
        errors, _ = self.validate_text(
            build_case001_arm_c_record(required_numbers=[1, 2, 3])
        )
        self.assertTrue(any("6.1..6.9" in error for error in errors), errors)

    def test_artifact_identity_and_contamination_fail(self) -> None:
        errors, _ = self.validate_text(
            build_case001_arm_c_record(
                artifact_name="cognitive-dogfood-case-001-arm-a",
                artifact_head="NOT-A-SHA",
                artifact_digest="sha256:bad",
                contamination="operator manifest was visible",
            )
        )
        expected_fragments = (
            "Known contamination must be none",
            "Execution artifact name does not match",
            "workflow head must be a 40-character",
            "artifact digest must use",
        )
        for fragment in expected_fragments:
            self.assertTrue(any(fragment in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
