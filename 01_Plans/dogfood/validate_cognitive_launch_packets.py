#!/usr/bin/env python3
"""Fail-closed checks for cognitive-dogfood launch-packet treatment equivalence.

This validator does not judge experiment results. It protects the frozen inputs for
Cases 001–003 so that the four arms differ by treatment, not by question/output or
product evidence snapshot.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

DOGFOOD_DIR = Path(__file__).parent
PRODUCT_COMMIT = "2232b3bb26647e5c4a083f55bdbf83c161698649"
SKILL_COMMIT = "3988e12e5f7f316f377d3391e9486c8467a111d5"
PRODUCT_SNAPSHOT = f"hat47x/kj-atlas@{PRODUCT_COMMIT}"
SKILL_SNAPSHOT = f"hat47x/cultural-substrate-weaving@{SKILL_COMMIT}"
VISIBLE_SKILL_BUNDLE_ID = f"cognitive-dogfood-skill-ja@{SKILL_COMMIT}"
OPERATOR_SKILL_MANIFEST_ID = f"case-001-skill-ja@{SKILL_COMMIT}"

MODES = {
    "ordinary": {"skill": False, "atlas": False},
    "skill": {"skill": True, "atlas": False},
    "atlas": {"skill": False, "atlas": True},
    "atlas-skill": {"skill": True, "atlas": True},
}


def extract_section(text: str, heading: str) -> str | None:
    pattern = re.compile(
        rf"(?ms)^## {re.escape(heading)}\s*\n(.*?)(?=^## |\Z)"
    )
    match = pattern.search(text)
    if not match:
        return None
    return match.group(1).strip()


def normalized(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.strip().splitlines())


def validate_case(case_number: str) -> list[str]:
    issues: list[str] = []
    case_id = f"case-{case_number}"
    expected_bundle = f"{case_id}-r1-product@{PRODUCT_COMMIT}"
    expected_starter = f"doc_cognitive_case_{case_number}_starter.json"
    label = f"Case {case_number}"

    questions: dict[str, str] = {}
    required_outputs: dict[str, str] = {}

    for mode, treatment in MODES.items():
        path = DOGFOOD_DIR / f"cognitive-dogfood-{case_id}-launch-{mode}.md"
        if not path.is_file():
            issues.append(f"{label} {mode}: missing launch packet {path.name}")
            continue

        text = path.read_text(encoding="utf-8")

        if "- Status: Frozen before" not in text:
            issues.append(f"{label} {mode}: launch packet is not marked frozen")
        if expected_bundle not in text:
            issues.append(f"{label} {mode}: product evidence bundle changed")
        if PRODUCT_SNAPSHOT not in text:
            issues.append(f"{label} {mode}: product snapshot changed")

        question = extract_section(text, "Fixed question")
        if not question:
            issues.append(f"{label} {mode}: missing Fixed question section")
        else:
            questions[mode] = normalized(question)

        required = extract_section(text, "Required output")
        if not required:
            issues.append(f"{label} {mode}: missing Required output section")
        else:
            required_outputs[mode] = normalized(required)

        has_skill = SKILL_SNAPSHOT in text
        has_starter = expected_starter in text
        if has_skill != treatment["skill"]:
            expectation = "must include" if treatment["skill"] else "must not include"
            issues.append(
                f"{label} {mode}: {expectation} frozen cultural-substrate-weaving treatment"
            )
        if has_starter != treatment["atlas"]:
            expectation = "must include" if treatment["atlas"] else "must not include"
            issues.append(f"{label} {mode}: {expectation} KJ Atlas starter document")

        # The preregistered source manifest remains Case-001-scoped for operator use,
        # but arm-visible skill bundles are intentionally case-neutral. A stale
        # operator manifest ID in launch.md makes the packet disagree with the
        # generated skill-bundle-manifest and can reveal irrelevant provenance.
        if OPERATOR_SKILL_MANIFEST_ID in text:
            issues.append(
                f"{label} {mode}: operator-only skill manifest ID leaked into launch packet"
            )
        if "Skill bundle ID:" in text:
            if not treatment["skill"]:
                issues.append(f"{label} {mode}: non-skill arm names a skill bundle ID")
            elif VISIBLE_SKILL_BUNDLE_ID not in text:
                issues.append(
                    f"{label} {mode}: Skill bundle ID does not match arm-visible manifest ID"
                )

        if "Candidate source request" not in text:
            issues.append(f"{label} {mode}: missing common candidate-source escape hatch")

    if len(questions) == len(MODES):
        baseline = questions["ordinary"]
        for mode, question in questions.items():
            if question != baseline:
                issues.append(
                    f"{label}: Fixed question differs between ordinary and {mode}"
                )

    if len(required_outputs) == len(MODES):
        baseline = required_outputs["ordinary"]
        for mode, required in required_outputs.items():
            if required != baseline:
                issues.append(
                    f"{label}: Required output differs between ordinary and {mode}"
                )

    return issues


def main() -> int:
    issues: list[str] = []
    for case_number in ("001", "002", "003"):
        issues.extend(validate_case(case_number))

    if issues:
        print(f"COGNITIVE LAUNCH PACKET ISSUES ({len(issues)}):")
        for issue in issues:
            print(f"  - {issue}")
        return 1

    print(
        "COGNITIVE LAUNCH PACKETS FROZEN AND TREATMENT-EQUIVALENT "
        "(Cases 001–003 / A–D) ✅"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
