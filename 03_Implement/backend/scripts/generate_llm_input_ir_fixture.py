#!/usr/bin/env python3
"""Regenerate the LLM input IR regression fixture (`llm_input_ir_spec.md` §6).

The spec's AC-1 / AC-4 require the fixture to be derivable from the spec alone
and without any LLM: this script only runs the deterministic projection in
`kj_atlas_api.llm_input_ir`, so `KJ_ATLAS_LLM_PROVIDER=none` is irrelevant here.

Usage (from `03_Implement/backend`):

    python3 scripts/generate_llm_input_ir_fixture.py
    python3 scripts/generate_llm_input_ir_fixture.py --check
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_BACKEND_ROOT / "src"))

from kj_atlas_api.llm_input_ir import (  # noqa: E402
    IR_VERSION,
    build_llm_input_ir,
    ir_sha256,
    source_from_document,
    validate_llm_input_ir,
)
from kj_atlas_api.models import DocumentV1  # noqa: E402

FIXTURE_DIR = _BACKEND_ROOT / "tests" / "fixtures"
DOCUMENT_PATH = FIXTURE_DIR / "llm_input_ir_document_v1_1.json"
EXPECTED_PATH = FIXTURE_DIR / "llm_input_ir_expected_v1_1.json"


def build_expected() -> dict[str, object]:
    document = DocumentV1.model_validate(json.loads(DOCUMENT_PATH.read_text(encoding="utf-8")))
    # `detect-contradiction` does not request coordinates (spec §2.2.1), so the
    # fixture exercises the coordinate-free shape that ADR-0069 D1=B enables.
    ir = build_llm_input_ir(source_from_document(document), include_coordinates=False)
    validate_llm_input_ir(ir)
    return {
        "generatedFrom": DOCUMENT_PATH.name,
        "irVersion": IR_VERSION,
        "sha256": ir_sha256(ir),
        "ir": ir,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit non-zero if the fixture on disk differs from the regenerated one",
    )
    args = parser.parse_args()

    expected = build_expected()
    serialized = json.dumps(expected, ensure_ascii=False, indent=2, sort_keys=True) + "\n"

    if args.check:
        current = EXPECTED_PATH.read_text(encoding="utf-8") if EXPECTED_PATH.exists() else ""
        if current != serialized:
            print(f"{EXPECTED_PATH} is stale; rerun without --check", file=sys.stderr)
            return 1
        print(f"{EXPECTED_PATH.name} is up to date (sha256={expected['sha256']})")
        return 0

    EXPECTED_PATH.write_text(serialized, encoding="utf-8")
    print(f"wrote {EXPECTED_PATH} (sha256={expected['sha256']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
