#!/usr/bin/env python3
"""Build a reviewer-facing blind package from a cognitive dogfood run record.

The builder copies only the common result-bearing sections. It intentionally
omits arm/method metadata, M1-M9 self-evaluation, InquiryJourney/T9 records, and
skill execution records. It does not paraphrase the run's claims.
"""

from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path

FORBIDDEN_DIRECT_MARKERS = (
    "cultural-substrate-weaving",
    "Arm A",
    "Arm B",
    "Arm C",
    "Arm D",
    "Activation verdict",
    "Framework candidates considered",
)


def parse_fields(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in text.splitlines():
        match = re.match(r"^- ([^:]+):\s*(.*)$", line)
        if match and match.group(1) not in result:
            result[match.group(1)] = match.group(2).strip()
    return result


def extract_section(text: str, start: str, next_heading: str | None) -> str:
    start_index = text.find(start)
    if start_index < 0:
        raise ValueError(f"missing section: {start}")
    if next_heading is None:
        return text[start_index:].strip()
    end_index = text.find(next_heading, start_index + len(start))
    if end_index < 0:
        raise ValueError(f"missing next section after {start}: {next_heading}")
    return text[start_index:end_index].strip()


def extract_until_any(text: str, start: str, next_headings: tuple[str, ...]) -> str:
    start_index = text.find(start)
    if start_index < 0:
        raise ValueError(f"missing section: {start}")
    candidates = [
        index
        for heading in next_headings
        if (index := text.find(heading, start_index + len(start))) >= 0
    ]
    if not candidates:
        raise ValueError(
            f"missing next section after {start}: one of {next_headings!r}"
        )
    return text[start_index:min(candidates)].strip()


def neutralize_conflict_section(section: str) -> str:
    """Hide preregistered test IDs without paraphrasing the run observation."""
    section = section.replace(
        "## 7. Conflict-bearing source check", "## Source correction observations"
    )
    counter = 0

    def replace_detected(match: re.Match[str]) -> str:
        nonlocal counter
        counter += 1
        verdict = match.group(2)
        return f"- source-check-{counter} detected: {verdict}"

    return re.sub(
        r"^- ([A-Za-z0-9-]+) detected:\s*(yes|no|partial)\s*$",
        replace_detected,
        section,
        flags=re.MULTILINE | re.IGNORECASE,
    )


def build_package(record_text: str) -> tuple[str, list[str]]:
    fields = parse_fields(record_text)
    alias = fields.get("Blind alias", "").strip()
    case_id = fields.get("Case ID", "").strip()
    round_id = fields.get("Round", "").strip()

    if not alias or alias.lower() in {"pending", "a", "b", "c", "d"}:
        raise ValueError("Blind alias must be assigned and neutral")
    if not case_id or not round_id:
        raise ValueError("Case ID and Round are required")

    fixed_question = extract_section(
        record_text, "## 1. Fixed question", "## 2. Input verification"
    )
    required_output = extract_section(
        record_text, "## 6. Required output", "## 7. Conflict-bearing source check"
    )
    conflict_observations = extract_section(
        record_text, "## 7. Conflict-bearing source check", "## 8. M1–M9 evidence"
    )
    candidate_sources = extract_until_any(
        record_text,
        "## 11. Candidate source requests",
        (
            "## 12. cultural-substrate-weaving execution record",
            "## 13. Static intake validation",
        ),
    )

    conflict_observations = neutralize_conflict_section(conflict_observations)
    source_digest = hashlib.sha256(record_text.encode("utf-8")).hexdigest()

    package = "\n\n".join(
        [
            "# Cognitive Dogfood Blind Package",
            (
                f"- Case ID: {case_id}\n"
                f"- Round: {round_id}\n"
                f"- Blind alias: {alias}\n"
                f"- Source record SHA-256: `{source_digest}`\n"
                "- Package scope: common result-bearing sections only"
            ),
            fixed_question,
            required_output,
            conflict_observations,
            candidate_sources,
            (
                "## Reviewer boundary\n\n"
                "This package intentionally omits arm identity, method metadata, "
                "run self-scoring, InquiryJourney/T9 records, skill execution "
                "records, and preregistered experimenter test identifiers. Review "
                "claims against the common frozen source bundle before any unblinding."
            ),
        ]
    ) + "\n"

    warnings: list[str] = []
    for marker in FORBIDDEN_DIRECT_MARKERS:
        if marker.lower() in package.lower():
            warnings.append(
                f"method identity may be inferable: direct marker {marker!r} remains"
            )

    return package, warnings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a blind review package from a cognitive dogfood run record."
    )
    parser.add_argument("record", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    if not args.record.is_file():
        print(f"FAIL: record not found: {args.record}")
        return 1

    record_text = args.record.read_text(encoding="utf-8")
    try:
        package, warnings = build_package(record_text)
    except ValueError as exc:
        print(f"FAIL: {exc}")
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(package, encoding="utf-8")
    package_digest = hashlib.sha256(package.encode("utf-8")).hexdigest()

    for warning in warnings:
        print(f"WARN: {warning}")
    print(f"WROTE: {args.output}")
    print(f"PACKAGE_SHA256: {package_digest}")
    print("NOTE: warnings require manual redaction review; do not paraphrase claims.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
