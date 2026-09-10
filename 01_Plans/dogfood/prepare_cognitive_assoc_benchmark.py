#!/usr/bin/env python3
"""Prepare model-blind inputs for COGNITIVE-ASSOC-01.

This utility deliberately does *not* run a semantic model. It validates the
frozen source manifest, strips grouping leakage from card inputs, and derives
the complete cross-island contrast pool for human adjudication.

The semantic baseline gate stays closed while the manifest status is
``pre_adjudication_frozen``. A later benchmark revision may explicitly open the
gate after maintainer adjudication has been committed.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ALLOWED_MODEL_FIELDS = ("documentId", "cardId", "text")
ADJUDICATION_LABELS = (
    "hard_negative",
    "related_but_separate",
    "ambiguous_or_held",
    "exclude",
)


@dataclass(frozen=True)
class PreparedSource:
    document_id: str
    cards: tuple[dict[str, str], ...]
    positive_sets: tuple[tuple[str, ...], ...]
    residuals: tuple[str, ...]


def git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require_manifest_contract(manifest: dict[str, Any]) -> None:
    contract = manifest.get("inputContract", {})
    visible = tuple(contract.get("modelVisibleFields", ()))
    if visible != ALLOWED_MODEL_FIELDS:
        raise ValueError(
            f"modelVisibleFields must be exactly {ALLOWED_MODEL_FIELDS!r}, got {visible!r}"
        )
    if contract.get("eligibility") != (
        "Only cards with textReviewed=true may enter model evaluation in benchmark v0."
    ):
        raise ValueError("benchmark v0 eligibility contract changed")
    if contract.get("noModelRunBeforeAdjudication") is not True:
        raise ValueError("pre-adjudication benchmark must keep semantic execution closed")
    if manifest.get("status") != "pre_adjudication_frozen":
        raise ValueError(
            "this preparer only accepts the frozen pre-adjudication v0 manifest"
        )


def source_exclusions(spec: dict[str, Any]) -> set[str]:
    excluded: set[str] = set()
    for entry in spec.get("excludedFromV0", []):
        card_id = entry.get("cardId")
        if not isinstance(card_id, str) or not card_id:
            raise ValueError("excludedFromV0 entry is missing cardId")
        excluded.add(card_id)
    return excluded


def prepare_source(repo_root: Path, spec: dict[str, Any]) -> PreparedSource:
    path = repo_root / spec["path"]
    raw = path.read_bytes()
    actual_sha = git_blob_sha(raw)
    expected_sha = spec["blobSha"]
    if actual_sha != expected_sha:
        raise ValueError(
            f"source blob mismatch for {spec['path']}: expected {expected_sha}, got {actual_sha}"
        )

    document = json.loads(raw.decode("utf-8"))
    if document.get("id") != spec["documentId"]:
        raise ValueError(
            f"document id mismatch for {spec['path']}: {document.get('id')!r}"
        )

    excluded = source_exclusions(spec)
    cards: list[dict[str, str]] = []
    reviewed_ids: set[str] = set()
    for card in document.get("cards", []):
        card_id = card.get("id")
        if not isinstance(card_id, str) or not card_id:
            raise ValueError(f"invalid card id in {spec['path']}")
        if card_id in excluded:
            continue
        if card.get("textReviewed") is not True:
            raise ValueError(
                f"unreviewed card {spec['documentId']}:{card_id} is eligible for v0; fail closed"
            )
        text = card.get("text")
        if not isinstance(text, str) or not text.strip():
            raise ValueError(f"empty card text: {spec['documentId']}:{card_id}")
        reviewed_ids.add(card_id)
        cards.append(
            {
                "documentId": spec["documentId"],
                "cardId": card_id,
                "text": text,
            }
        )

    expected_count = spec.get("reviewedCardCount")
    source_card_count = len(document.get("cards", []))
    if not isinstance(expected_count, int) or expected_count != source_card_count:
        raise ValueError(
            f"reviewedCardCount must describe the frozen source before explicit exclusions: "
            f"expected {expected_count!r}, source has {source_card_count} cards"
        )

    positive_sets: list[tuple[str, ...]] = []
    seen_positive_cards: set[str] = set()
    for positive in spec.get("observedPositiveSets", []):
        card_ids = tuple(positive.get("cardIds", ()))
        if len(card_ids) < 2:
            raise ValueError("observedPositiveSet must contain at least two cards")
        unknown = set(card_ids) - reviewed_ids
        if unknown:
            raise ValueError(
                f"observedPositiveSet references excluded/unknown cards in {spec['documentId']}: "
                f"{sorted(unknown)}"
            )
        overlap = seen_positive_cards.intersection(card_ids)
        if overlap:
            raise ValueError(
                f"v0 expects disjoint observed source islands; duplicated cards: {sorted(overlap)}"
            )
        seen_positive_cards.update(card_ids)
        positive_sets.append(card_ids)

    residuals = tuple(spec.get("observedResiduals", ()))
    unknown_residuals = set(residuals) - reviewed_ids
    if unknown_residuals:
        raise ValueError(
            f"observedResiduals reference excluded/unknown cards: {sorted(unknown_residuals)}"
        )
    if set(residuals).intersection(seen_positive_cards):
        raise ValueError("a card cannot be both observedPositive and observedResidual")

    challenge_sets = spec.get("challengePositiveSets", [])
    positive_memberships = [set(group) for group in positive_sets]
    for challenge in challenge_sets:
        challenge_set = set(challenge)
        if not any(challenge_set.issubset(group) for group in positive_memberships):
            raise ValueError(
                f"challengePositiveSet crosses observed islands in {spec['documentId']}: {challenge}"
            )

    return PreparedSource(
        document_id=spec["documentId"],
        cards=tuple(sorted(cards, key=lambda card: card["cardId"])),
        positive_sets=tuple(positive_sets),
        residuals=residuals,
    )


def island_index(source: PreparedSource) -> dict[str, str | None]:
    result: dict[str, str | None] = {card["cardId"]: None for card in source.cards}
    for index, group in enumerate(source.positive_sets, start=1):
        for card_id in group:
            result[card_id] = f"observed-{index}"
    for card_id in source.residuals:
        result[card_id] = "residual"
    return result


def derive_pair_pool(source: PreparedSource) -> list[dict[str, Any]]:
    membership = island_index(source)
    ids = [card["cardId"] for card in source.cards]
    result: list[dict[str, Any]] = []
    for left, right in itertools.combinations(ids, 2):
        left_group = membership[left]
        right_group = membership[right]
        if left_group is not None and left_group == right_group:
            continue
        result.append(
            {
                "id": f"{source.document_id}:pair:{left}+{right}",
                "documentId": source.document_id,
                "cardIds": [left, right],
                "label": "pending_human",
                "allowedLabels": list(ADJUDICATION_LABELS),
            }
        )
    return result


def derive_two_plus_one_pool(source: PreparedSource) -> list[dict[str, Any]]:
    all_ids = {card["cardId"] for card in source.cards}
    result: list[dict[str, Any]] = []
    for group_index, group in enumerate(source.positive_sets, start=1):
        outsiders = sorted(all_ids - set(group))
        for left, right in itertools.combinations(sorted(group), 2):
            for outsider in outsiders:
                result.append(
                    {
                        "id": (
                            f"{source.document_id}:2plus1:g{group_index}:"
                            f"{left}+{right}+{outsider}"
                        ),
                        "documentId": source.document_id,
                        "cardIds": [left, right, outsider],
                        "label": "pending_human",
                        "allowedLabels": list(ADJUDICATION_LABELS),
                    }
                )
    return result


def prepare(manifest_path: Path, repo_root: Path) -> tuple[list[dict[str, str]], dict[str, Any]]:
    manifest = load_json(manifest_path)
    require_manifest_contract(manifest)
    sources = [prepare_source(repo_root, spec) for spec in manifest.get("sources", [])]
    if not sources:
        raise ValueError("manifest has no sources")

    model_input = [card for source in sources for card in source.cards]
    for card in model_input:
        if tuple(card.keys()) != ALLOWED_MODEL_FIELDS:
            raise AssertionError(f"model input leaked fields: {tuple(card.keys())!r}")

    pair_pool = [candidate for source in sources for candidate in derive_pair_pool(source)]
    two_plus_one_pool = [
        candidate for source in sources for candidate in derive_two_plus_one_pool(source)
    ]
    adjudication = {
        "benchmarkId": manifest["id"],
        "status": "pending_human",
        "semanticBaselineGate": "closed",
        "modelOutputsAllowed": False,
        "pairCandidates": pair_pool,
        "twoPlusOneCandidates": two_plus_one_pool,
    }
    return model_input, adjudication


def write_outputs(
    model_input: list[dict[str, str]], adjudication: dict[str, Any], output_dir: Path
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    corpus_path = output_dir / "model-input.jsonl"
    corpus_text = "".join(
        json.dumps(card, ensure_ascii=False, separators=(",", ":")) + "\n"
        for card in model_input
    )
    corpus_path.write_text(corpus_text, encoding="utf-8")

    adjudication_path = output_dir / "contrast-pool.json"
    adjudication_path.write_text(
        json.dumps(adjudication, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"WROTE: {corpus_path}")
    print(f"WROTE: {adjudication_path}")
    print(f"MODEL_INPUT_COUNT: {len(model_input)}")
    print(f"PAIR_CANDIDATE_COUNT: {len(adjudication['pairCandidates'])}")
    print(f"TWO_PLUS_ONE_CANDIDATE_COUNT: {len(adjudication['twoPlusOneCandidates'])}")
    print("SEMANTIC_BASELINE_GATE: CLOSED (maintainer adjudication required)")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepare blind inputs and a human-only contrast pool for COGNITIVE-ASSOC-01."
    )
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    try:
        model_input, adjudication = prepare(
            args.manifest.resolve(), args.repo_root.resolve()
        )
        write_outputs(model_input, adjudication, args.output_dir.resolve())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
