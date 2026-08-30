#!/usr/bin/env python3
"""Static intake validation for cognitive dogfood run records.

This validates experiment comparability/record completeness only. It does not
score cognitive quality or choose a winning arm. Case-specific fixed questions,
source manifest IDs, and preregistered conflict-check IDs are frozen here for
Cases 001–003.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

PRODUCT_SHA = "2232b3bb26647e5c4a083f55bdbf83c161698649"
SKILL_SHA = "3988e12e5f7f316f377d3391e9486c8467a111d5"
EXPECTED_ORDER = {"C": 1, "D": 2, "B": 3, "A": 4}

CASE_CONTRACTS = {
    "case-001": {
        "question": (
            "KJ Atlasは、既存のAIチャット、ホワイトボード、質的分析ツール、文書/issue管理では十分に満たしにくい、"
            "どの利用仕事のために存在するべきか。現在の設計・実装・dogfoodは、その価値をどこまで実現し、"
            "何をまだ実証できていないか。"
        ),
        "tests": ("T1", "T2", "T3"),
    },
    "case-002": {
        "question": (
            "KJ Atlasのカード化、束ね、表札、反対視点、空白探索、配置、叙述などのAI支援について、"
            "どこまでを提案・自動化し、どこで人間の判断・確認・有益な摩擦を必須とするべきか。"
            "現在のproposal-only原則は、操作ごとの誤り方と利用価値に対して粗すぎないか、"
            "または十分に一般的な安全境界か。"
        ),
        "tests": ("C2-T1", "C2-T2", "C2-T3", "C2-T4"),
    },
    "case-003": {
        "question": (
            "KJ Atlasはoffline/local/self-hostによるデータ統制と、共同分析・共有・組織導入に必要な"
            "同期/collaborationをどの境界で両立するべきか。local-firstを中核価値、配備オプション、"
            "安全境界、または特定利用ケース向け要件のどれとして扱うべきか。"
        ),
        "tests": ("C3-T1", "C3-T2", "C3-T3", "C3-T4", "C3-T5"),
    },
}

CASE_ALIASES = {
    "001": "case-001",
    "case 001": "case-001",
    "case-001": "case-001",
    "002": "case-002",
    "case 002": "case-002",
    "case-002": "case-002",
    "003": "case-003",
    "case 003": "case-003",
    "case-003": "case-003",
}

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


def normalize_case_id(raw: str) -> str | None:
    return CASE_ALIASES.get(raw.strip().lower())


def section_text(text: str, start: str, end: str) -> str:
    start_index = text.find(start)
    if start_index < 0:
        return ""
    end_index = text.find(end, start_index + len(start))
    if end_index < 0:
        return ""
    return text[start_index + len(start):end_index].strip()


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

    raw_case_id = fields.get("Case ID", "")
    case_id = normalize_case_id(raw_case_id)
    if case_id is None:
        errors.append(
            f"Case ID must identify one of {tuple(CASE_CONTRACTS)}, got {raw_case_id!r}"
        )
        contract = None
    else:
        contract = CASE_CONTRACTS[case_id]

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
            "KJ Atlas snapshot does not match the frozen cognitive-dogfood product SHA"
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

    if case_id is not None:
        expected_manifest = f"{case_id}-r1-product@{PRODUCT_SHA}"
        if fields.get("Source manifest ID", "").strip() != expected_manifest:
            errors.append(
                f"Source manifest ID does not match frozen {case_id} Round 1 manifest"
            )

    normalized_text = re.sub(r"\s+", " ", text)
    if contract is not None and contract["question"] not in normalized_text:
        errors.append(f"Fixed question is missing or changed for {case_id}")

    for heading in COMMON_HEADINGS:
        if heading not in text:
            errors.append(f"required heading missing: {heading}")

    required_output = section_text(
        text, "## 6. Required output", "## 7. Conflict-bearing source check"
    )
    if not required_output:
        errors.append("Required output section is empty or malformed")
    else:
        result_headings = re.findall(r"^### 6\.\d+\s+\S.*$", required_output, re.MULTILINE)
        if not result_headings:
            errors.append(
                "Required output must contain at least one populated '### 6.<n>' heading"
            )

    if contract is not None:
        expected_tests = tuple(contract["tests"])
        for test_id in expected_tests:
            pattern = rf"^- {re.escape(test_id)} detected:\s*(yes|no|partial)\s*$"
            if not re.search(pattern, text, re.MULTILINE | re.IGNORECASE):
                errors.append(f"{test_id} detected must be yes/no/partial")

        detected_test_lines = re.findall(
            r"^- ([A-Za-z0-9-]+) detected:\s*(?:yes|no|partial)\s*$",
            text,
            re.MULTILINE | re.IGNORECASE,
        )
        unexpected = [test for test in detected_test_lines if test not in expected_tests]
        if unexpected:
            errors.append(
                f"unexpected conflict-check IDs for {case_id}: {', '.join(unexpected)}"
            )

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
        description="Validate Case 001–003 Round 1 cognitive dogfood run records."
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
