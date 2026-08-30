#!/usr/bin/env python3
"""Static intake validation for cognitive dogfood run records.

This validates experiment comparability/record completeness only. It does not
score cognitive quality or choose a winning arm.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

PRODUCT_SHA = "2232b3bb26647e5c4a083f55bdbf83c161698649"
SKILL_SHA = "3988e12e5f7f316f377d3391e9486c8467a111d5"
SOURCE_MANIFEST_ID = f"case-001-r1-product@{PRODUCT_SHA}"
EXPECTED_ORDER = {"C": 1, "D": 2, "B": 3, "A": 4}
FIXED_QUESTION = (
    "KJ Atlasは、既存のAIチャット、ホワイトボード、質的分析ツール、文書/issue管理では十分に満たしにくい、"
    "どの利用仕事のために存在するべきか。現在の設計・実装・dogfoodは、その価値をどこまで実現し、"
    "何をまだ実証できていないか。"
)

REQUIRED_META = [
    "Case ID",
    "Round",
    "Arm",
    "Blind alias",
    "Run ID",
    "Run validity",
    "Date",
    "Execution order position",
    "Operator",
    "Model/provider",
    "KJ Atlas version/commit",
    "cultural-substrate-weaving version/commit",
    "Source manifest ID",
    "Operator pack/version",
    "Context started fresh",
    "Known contamination",
]

COMMON_HEADINGS = [
    "## 1. Fixed question",
    "## 2. Input verification",
    "## 3. Pre-analysis state",
    "## 4. Raw analysis artifacts",
    "## 5. AI proposal ledger",
    "## 6. Required output",
    "### 6.1 利用者の仕事",
    "### 6.2 既存手段との境界",
    "### 6.3 現在実現している価値",
    "### 6.4 未実証の価値仮説",
    "### 6.5 KJ Atlasが不要かもしれない条件",
    "### 6.6 次の検証/issue",
    "### 6.7 訂正・矛盾・旧情報",
    "### 6.8 保留",
    "## 7. Conflict-bearing source check",
    "## 8. M1–M9 evidence",
    "### M1 生存所見",
    "### M2 根拠接地",
    "### M3 異論・残差保持",
    "### M4 早期収束耐性",
    "### M5 AI依存校正",
    "### M6 再訪・訂正可能性",
    "### M7 注意・探索制御",
    "### M8 決定への変換品質",
    "### M9 認知摩擦",
    "## 9. Retention audit",
    "## 11. Candidate source requests",
    "## 13. Static intake validation",
]


def parse_fields(text: str) -> dict[str, str]:
    """Return the first Markdown '- key: value' occurrence for each key."""
    result: dict[str, str] = {}
    for line in text.splitlines():
        match = re.match(r"^- ([^:]+):\s*(.*)$", line)
        if match and match.group(1) not in result:
            result[match.group(1)] = match.group(2).strip()
    return result


def blank_or_placeholder(value: str) -> bool:
    value = value.strip()
    return not value or (value.startswith("<") and value.endswith(">"))


def validate_record(path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    text = path.read_text(encoding="utf-8")
    fields = parse_fields(text)

    for key in REQUIRED_META:
        if key not in fields or blank_or_placeholder(fields[key]):
            errors.append(f"metadata missing/placeholder: {key}")

    arm = fields.get("Arm", "").strip().upper()
    if arm not in {"A", "B", "C", "D"}:
        errors.append(f"Arm must be A/B/C/D, got {arm!r}")

    case_id = fields.get("Case ID", "").strip().lower()
    if case_id not in {"case-001", "001", "case 001"}:
        errors.append(f"Case ID must identify case-001, got {case_id!r}")

    round_id = fields.get("Round", "").strip().lower()
    if round_id not in {"1", "round 1"}:
        errors.append(f"Round must be 1 for this validator, got {round_id!r}")

    if fields.get("Run validity", "").strip().lower() != "valid":
        errors.append("Run validity must be 'valid' before P2 blind review")

    if fields.get("Context started fresh", "").strip().lower() != "yes":
        errors.append("Context started fresh must be yes")

    contamination = fields.get("Known contamination", "").strip().lower()
    if contamination not in {"none", "none known", "no", "なし"}:
        errors.append(
            "Known contamination must be none for a valid run, "
            f"got {contamination!r}"
        )

    blind_alias = fields.get("Blind alias", "").strip()
    if blind_alias.lower() in {"pending", "a", "b", "c", "d"}:
        errors.append("Blind alias must be a neutral assigned alias before P2")

    order_text = fields.get("Execution order position", "").strip()
    order_match = re.match(r"^(\d+)(?:\s*/\s*4)?$", order_text)
    if arm in EXPECTED_ORDER:
        if not order_match:
            errors.append(
                "Execution order position must be an integer 1..4 or '<n>/4'"
            )
        elif int(order_match.group(1)) != EXPECTED_ORDER[arm]:
            errors.append(
                f"Arm {arm} must be execution position {EXPECTED_ORDER[arm]} "
                "under the preregistered C→D→B→A order"
            )

    if PRODUCT_SHA not in fields.get("KJ Atlas version/commit", ""):
        errors.append(
            "KJ Atlas snapshot does not match the frozen Case 001 Round 1 SHA"
        )

    skill_version = fields.get(
        "cultural-substrate-weaving version/commit", ""
    ).strip()
    if arm in {"B", "D"}:
        if SKILL_SHA not in skill_version:
            errors.append("B/D skill snapshot does not match the frozen SHA")
    elif arm in {"A", "C"}:
        if skill_version.lower() not in {"n/a", "na", "none"}:
            errors.append(
                "A/C must record cultural-substrate-weaving version as N/A"
            )

    if fields.get("Source manifest ID", "").strip() != SOURCE_MANIFEST_ID:
        errors.append(
            "Source manifest ID does not match the frozen Case 001 Round 1 manifest"
        )

    normalized_text = re.sub(r"\s+", " ", text)
    if FIXED_QUESTION not in normalized_text:
        errors.append("Fixed question is missing or changed")

    for heading in COMMON_HEADINGS:
        if heading not in text:
            errors.append(f"required heading missing: {heading}")

    for test_id in ("T1", "T2", "T3"):
        pattern = rf"^- {test_id} detected:\s*(yes|no|partial)\s*$"
        if not re.search(pattern, text, re.MULTILINE | re.IGNORECASE):
            errors.append(f"{test_id} detected must be yes/no/partial")

    if arm in {"C", "D"}:
        if "## 10. InquiryJourney actual-use record (C/D only)" not in text:
            errors.append("C/D requires InquiryJourney actual-use section")
        for label in (
            "KJ Atlas document ID/file",
            "InquiryJourney/bundle reference",
        ):
            value = fields.get(label)
            if value is None or blank_or_placeholder(value):
                errors.append(f"C/D raw artifact reference missing: {label}")

    if arm in {"B", "D"}:
        skill_heading = (
            "## 12. cultural-substrate-weaving execution record (B/D only)"
        )
        if skill_heading not in text:
            errors.append("B/D requires skill execution section")
        for label in (
            "Activation verdict",
            "Activation reason",
            "Framework candidates considered",
            "Selected framework(s) and reason",
            "Rejected framework(s) and reason",
            "Removal test — framework terminology removed",
            "Substitution test — alternative framework/baseline could produce same finding",
            "Skill-specific surviving findings after removal/substitution",
            "Stop condition reached",
        ):
            value = fields.get(label)
            if value is None or blank_or_placeholder(value):
                errors.append(f"B/D skill record missing: {label}")

    unresolved_placeholders = []
    for line_number, line in enumerate(text.splitlines(), 1):
        if re.search(r"<[^>]+>", line):
            unresolved_placeholders.append(line_number)
    if unresolved_placeholders:
        shown = ", ".join(str(n) for n in unresolved_placeholders[:12])
        errors.append(f"unresolved angle-bracket placeholders at lines: {shown}")

    stem = path.stem.lower()
    if stem in {"a-record", "b-record", "c-record", "d-record", "a", "b", "c", "d"}:
        warnings.append("filename appears to expose arm identity; use a neutral alias")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Case 001 Round 1 cognitive dogfood run records."
    )
    parser.add_argument("records", nargs="+", type=Path)
    args = parser.parse_args()

    failed = 0
    for record in args.records:
        print(f"=== {record} ===")
        if not record.is_file():
            print("FAIL: file not found")
            failed += 1
            continue

        errors, warnings = validate_record(record)
        for warning in warnings:
            print(f"WARN: {warning}")
        for error in errors:
            print(f"FAIL: {error}")

        if errors:
            failed += 1
            print(
                f"RESULT: FAIL ({len(errors)} errors, {len(warnings)} warnings)"
            )
        else:
            print(f"RESULT: PASS (0 errors, {len(warnings)} warnings)")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
