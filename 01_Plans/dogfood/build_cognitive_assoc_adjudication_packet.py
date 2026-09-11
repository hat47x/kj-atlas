#!/usr/bin/env python3
"""Build a model-blind human adjudication packet for COGNITIVE-ASSOC-01.

The packet is intentionally boring: deterministic candidate order, card text,
and the preregistered four-way human label only. It must not contain source
island labels/titles, coordinates, graph relations, semantic scores, model
rankings, or model-generated explanations.

This utility consumes outputs from prepare_cognitive_assoc_benchmark.py while
its semantic baseline gate is CLOSED. It cannot open that gate and cannot
produce an adjudicated benchmark by itself; the maintainer must write the
judgements explicitly.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ALLOWED_LABELS = (
    "hard_negative",
    "related_but_separate",
    "ambiguous_or_held",
    "exclude",
)

FORBIDDEN_KEYS = {
    "islandId",
    "islandTitle",
    "sourceIslandId",
    "x",
    "y",
    "geometry",
    "edges",
    "score",
    "similarity",
    "distance",
    "activation",
    "confidence",
    "ranking",
    "modelOutput",
    "modelExplanation",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_model_input(path: Path) -> dict[tuple[str, str], str]:
    cards: dict[tuple[str, str], str] = {}
    for line_no, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw_line.strip():
            continue
        card = json.loads(raw_line)
        if set(card) != {"documentId", "cardId", "text"}:
            raise ValueError(
                f"model-input line {line_no} contains unexpected fields: {sorted(card)}"
            )
        key = (card["documentId"], card["cardId"])
        if key in cards:
            raise ValueError(f"duplicate model-input card: {key}")
        text = card["text"]
        if not isinstance(text, str) or not text.strip():
            raise ValueError(f"empty model-input text: {key}")
        cards[key] = text
    if not cards:
        raise ValueError("model-input is empty")
    return cards


def assert_no_forbidden_keys(value: Any, path: str = "root") -> None:
    if isinstance(value, dict):
        forbidden = FORBIDDEN_KEYS.intersection(value)
        if forbidden:
            raise ValueError(
                f"contrast input leaks forbidden fields at {path}: {sorted(forbidden)}"
            )
        for key, child in value.items():
            assert_no_forbidden_keys(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            assert_no_forbidden_keys(child, f"{path}[{index}]")


def validate_contrast_pool(pool: dict[str, Any]) -> None:
    assert_no_forbidden_keys(pool)
    if pool.get("status") != "pending_human":
        raise ValueError("contrast pool must still be pending_human")
    if pool.get("semanticBaselineGate") != "closed":
        raise ValueError("semantic baseline gate must remain closed")
    if pool.get("modelOutputsAllowed") is not False:
        raise ValueError("model outputs must remain forbidden during adjudication")

    seen: set[str] = set()
    for collection_name in ("pairCandidates", "twoPlusOneCandidates"):
        collection = pool.get(collection_name)
        if not isinstance(collection, list):
            raise ValueError(f"missing candidate collection: {collection_name}")
        for candidate in collection:
            candidate_id = candidate.get("id")
            if not isinstance(candidate_id, str) or not candidate_id:
                raise ValueError(f"candidate without id in {collection_name}")
            if candidate_id in seen:
                raise ValueError(f"duplicate candidate id: {candidate_id}")
            seen.add(candidate_id)
            if candidate.get("label") != "pending_human":
                raise ValueError(
                    f"candidate already labelled before packet build: {candidate_id}"
                )
            if tuple(candidate.get("allowedLabels", ())) != ALLOWED_LABELS:
                raise ValueError(
                    f"candidate allowedLabels changed: {candidate_id}"
                )
            card_ids = candidate.get("cardIds")
            expected_size = 2 if collection_name == "pairCandidates" else 3
            if not isinstance(card_ids, list) or len(card_ids) != expected_size:
                raise ValueError(
                    f"candidate {candidate_id} must contain {expected_size} cards"
                )
            if len(set(card_ids)) != expected_size:
                raise ValueError(f"candidate repeats a card: {candidate_id}")


def render_candidate(
    candidate: dict[str, Any], cards: dict[tuple[str, str], str], ordinal: int
) -> str:
    document_id = candidate["documentId"]
    rendered_cards: list[str] = []
    for index, card_id in enumerate(candidate["cardIds"], 1):
        key = (document_id, card_id)
        if key not in cards:
            raise ValueError(
                f"candidate {candidate['id']} references missing blind card {key}"
            )
        rendered_cards.append(
            f"**Card {index} — `{card_id}`**\n\n{cards[key]}"
        )

    choices = " / ".join(f"`{label}`" for label in ALLOWED_LABELS)
    return (
        f"### {ordinal:04d}. `{candidate['id']}`\n\n"
        f"- Document: `{document_id}`\n"
        f"- Label: `PENDING`\n"
        f"- Choices: {choices}\n"
        f"- Reason: <!-- 任意。言語化できない場合は空欄でよい -->\n\n"
        + "\n\n".join(rendered_cards)
    )


def build_packet(
    pool: dict[str, Any], cards: dict[tuple[str, str], str]
) -> str:
    validate_contrast_pool(pool)

    candidates = sorted(
        pool["pairCandidates"] + pool["twoPlusOneCandidates"],
        key=lambda item: item["id"],
    )
    sections = [
        "# COGNITIVE-ASSOC-01 Contrast Human Adjudication Packet",
        "",
        f"- Benchmark: `{pool.get('benchmarkId', '')}`",
        "- State: model-blind / semantic baseline gate CLOSED",
        f"- Candidate count: {len(candidates)}",
        "- Allowed labels: `hard_negative` / `related_but_separate` / `ambiguous_or_held` / `exclude`",
        "",
        "## 判定境界",
        "",
        "このパケットは既存島の正解を再確認するためのものではない。島をまたぐ組合せについて、モデル結果を見る前に『一束として寄せないことが重要か』『関係はあるが別か』『まだ閉じないか』『評価から外すか』を記録する。",
        "",
        "表札を無理に書けない、理由を言語化できない場合は `ambiguous_or_held` を選べる。理由欄は任意であり、説明できないことを欠陥としない。",
        "",
        "島名・座標・relation・semantic score・モデル順位は意図的に含めない。",
        "",
        "---",
    ]

    for ordinal, candidate in enumerate(candidates, 1):
        sections.extend(["", render_candidate(candidate, cards, ordinal), "", "---"])

    return "\n".join(sections).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a deterministic model-blind human adjudication packet."
    )
    parser.add_argument("model_input", type=Path)
    parser.add_argument("contrast_pool", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    try:
        cards = load_model_input(args.model_input)
        pool = load_json(args.contrast_pool)
        packet = build_packet(pool, cards)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}")
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(packet, encoding="utf-8")
    count = len(pool["pairCandidates"]) + len(pool["twoPlusOneCandidates"])
    print(f"WROTE: {args.output}")
    print(f"CANDIDATE_COUNT: {count}")
    print("SEMANTIC_BASELINE_GATE: CLOSED")
    print("NEXT: maintainer adjudication; do not run semantic baselines yet")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
