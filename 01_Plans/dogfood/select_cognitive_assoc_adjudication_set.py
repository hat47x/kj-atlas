#!/usr/bin/env python3
"""Select a bounded, model-blind adjudication set for COGNITIVE-ASSOC-01.

Two preregistered strata are used:
- U: SHA-256 order of candidate ID (text-independent deterministic sample)
- L: character-trigram Jaccard stress sample (surface overlap only)

No semantic embedding, FlyHash output, LLM result, island title, coordinates, or
relation graph is consumed. Selection metadata is kept in the machine artifact
but the human-facing packet builder does not render it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import unicodedata
from pathlib import Path
from typing import Any

from build_cognitive_assoc_adjudication_packet import (
    ALLOWED_LABELS,
    load_model_input,
    validate_contrast_pool,
)

UNIFORM_N = 16
LEXICAL_N = 16


def normalized_chars(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    return "".join(ch for ch in text if ch.isalnum())


def trigrams(text: str) -> set[str]:
    normalized = normalized_chars(text)
    if len(normalized) < 3:
        return {normalized} if normalized else set()
    return {normalized[index : index + 3] for index in range(len(normalized) - 2)}


def jaccard(left: str, right: str) -> float:
    a = trigrams(left)
    b = trigrams(right)
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def stable_hash_key(candidate: dict[str, Any]) -> str:
    return hashlib.sha256(candidate["id"].encode("utf-8")).hexdigest()


def lexical_score(
    candidate: dict[str, Any], cards: dict[tuple[str, str], str]
) -> float:
    document_id = candidate["documentId"]
    ids = candidate["cardIds"]
    texts = [cards[(document_id, card_id)] for card_id in ids]
    if len(texts) == 2:
        return jaccard(texts[0], texts[1])
    if len(texts) == 3:
        outsider = texts[2]
        return max(jaccard(texts[0], outsider), jaccard(texts[1], outsider))
    raise ValueError(f"unsupported candidate width: {candidate['id']}")


def select_collection(
    candidates: list[dict[str, Any]],
    cards: dict[tuple[str, str], str],
    uniform_n: int = UNIFORM_N,
    lexical_n: int = LEXICAL_N,
) -> list[dict[str, Any]]:
    uniform = sorted(candidates, key=stable_hash_key)[:uniform_n]
    lexical = sorted(
        candidates,
        key=lambda candidate: (-lexical_score(candidate, cards), candidate["id"]),
    )[:lexical_n]

    selected: dict[str, dict[str, Any]] = {}
    for candidate in uniform:
        copy = dict(candidate)
        copy["selectionStrata"] = ["U"]
        selected[candidate["id"]] = copy
    for candidate in lexical:
        if candidate["id"] in selected:
            selected[candidate["id"]]["selectionStrata"].append("L")
        else:
            copy = dict(candidate)
            copy["selectionStrata"] = ["L"]
            selected[candidate["id"]] = copy

    return [selected[key] for key in sorted(selected)]


def select(pool: dict[str, Any], cards: dict[tuple[str, str], str]) -> dict[str, Any]:
    validate_contrast_pool(pool)
    pairs = select_collection(pool["pairCandidates"], cards)
    triples = select_collection(pool["twoPlusOneCandidates"], cards)
    result = {
        "benchmarkId": pool["benchmarkId"],
        "status": "pending_human",
        "semanticBaselineGate": "closed",
        "modelOutputsAllowed": False,
        "selectionProtocol": {
            "version": "cognitive-assoc-v0-u16-l16",
            "uniform": {
                "countPerCandidateType": UNIFORM_N,
                "ordering": "sha256(candidate.id) ascending",
            },
            "lexicalStress": {
                "countPerCandidateType": LEXICAL_N,
                "normalization": "Unicode NFKC; keep alphanumeric Unicode characters only",
                "feature": "character trigram set",
                "pair": "Jaccard overlap",
                "twoPlusOne": "max Jaccard(outsider, each in-island member)",
                "tieBreak": "candidate.id ascending",
            },
            "humanPacketHidesSelectionStrata": True,
        },
        "sourcePoolCounts": {
            "pairCandidates": len(pool["pairCandidates"]),
            "twoPlusOneCandidates": len(pool["twoPlusOneCandidates"]),
        },
        "pairCandidates": pairs,
        "twoPlusOneCandidates": triples,
    }
    validate_contrast_pool(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Select preregistered U/L human-adjudication strata without semantic models."
    )
    parser.add_argument("model_input", type=Path)
    parser.add_argument("contrast_pool", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    try:
        cards = load_model_input(args.model_input)
        pool = json.loads(args.contrast_pool.read_text(encoding="utf-8"))
        selected = select(pool, cards)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}")
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(selected, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    pair_count = len(selected["pairCandidates"])
    triple_count = len(selected["twoPlusOneCandidates"])
    print(f"WROTE: {args.output}")
    print(f"PAIR_REVIEW_COUNT: {pair_count}")
    print(f"TWO_PLUS_ONE_REVIEW_COUNT: {triple_count}")
    print(f"TOTAL_REVIEW_COUNT: {pair_count + triple_count}")
    print("SEMANTIC_BASELINE_GATE: CLOSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
