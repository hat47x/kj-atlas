#!/usr/bin/env python3
"""D1 lexical sparse candidate channel for formal SUI query snapshots.

D1 is deliberately surface-only. It performs no semantic inference and emits
no similarity score, confidence, importance, or rank. Candidates are ordered by
stable ref id; shared n-grams are evidence, not a value judgement.
"""

from __future__ import annotations

import copy
import unicodedata
from typing import Any, Iterable

from query_engine import D0Network, D0QueryError


class D1LexicalError(ValueError):
    pass


FORBIDDEN_RANKING_KEYS = {"score", "confidence", "importance", "rank"}


def _surface_chars(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text).casefold()
    return "".join(ch for ch in normalized if ch.isalnum())


def character_ngrams(text: str, sizes: tuple[int, ...] = (2, 3)) -> set[str]:
    """Return deterministic Unicode character n-gram features.

    Whitespace and punctuation are removed after NFKC + casefold. This is a
    surface lexical feature extractor; it must not be described as semantic.
    """

    surface = _surface_chars(text)
    grams: set[str] = set()
    for size in sorted(set(sizes)):
        if not isinstance(size, int) or size < 1:
            raise D1LexicalError("ngram sizes must be positive integers")
        for index in range(0, max(0, len(surface) - size + 1)):
            grams.add(surface[index : index + size])
    return grams


def _require_refs(network: D0Network, refs: Iterable[str], field: str) -> list[str]:
    normalized = sorted(set(refs))
    if not normalized:
        raise D1LexicalError(f"{field} must not be empty")
    unknown = [ref for ref in normalized if ref not in network.nodes]
    if unknown:
        raise D1LexicalError(f"{field} contains unknown refs: {unknown}")
    return normalized


def _text_features(network: D0Network, ref: str) -> set[str]:
    text = network.nodes[ref].get("text")
    if not isinstance(text, str) or not text.strip():
        return set()
    return character_ngrams(text)


def lexical_expand(
    network: D0Network,
    anchor_refs: Iterable[str],
    *,
    scope_refs: Iterable[str] | None = None,
    min_shared_features: int = 2,
    max_evidence_features: int = 12,
) -> dict[str, Any]:
    """Return surface-lexical candidates as an independent query channel.

    The threshold is an execution rule, not a user-visible similarity score.
    Results are sorted only by stable ref id. No candidate is auto-added to a
    canonical island/relation/consensus state.
    """

    anchors = _require_refs(network, anchor_refs, "anchorRefs")
    scope = (
        sorted(network.nodes)
        if scope_refs is None
        else _require_refs(network, scope_refs, "scopeRefs")
    )
    if not isinstance(min_shared_features, int) or min_shared_features < 1:
        raise D1LexicalError("min_shared_features must be a positive integer")
    if not isinstance(max_evidence_features, int) or max_evidence_features < 1:
        raise D1LexicalError("max_evidence_features must be a positive integer")

    anchor_features = {ref: _text_features(network, ref) for ref in anchors}
    items: list[dict[str, Any]] = []

    for ref in scope:
        if ref in anchors:
            continue
        candidate_features = _text_features(network, ref)
        if not candidate_features:
            continue

        matched_anchors: list[str] = []
        shared_features: set[str] = set()
        for anchor_ref in anchors:
            shared = candidate_features & anchor_features[anchor_ref]
            if len(shared) >= min_shared_features:
                matched_anchors.append(anchor_ref)
                shared_features.update(shared)

        if not matched_anchors:
            continue

        items.append(
            {
                "ref": ref,
                "matchedAnchorRefs": sorted(matched_anchors),
                "evidence": {
                    "sharedCharacterNgrams": sorted(shared_features)[:max_evidence_features]
                },
            }
        )

    items.sort(key=lambda item: item["ref"])
    result = {
        "channel": "lexical_sparse",
        "anchorRefs": anchors,
        "candidateRefs": [item["ref"] for item in items],
        "items": items,
        "trace": {
            "networkId": network.network_id,
            "method": "nfkc_casefold_unicode_alnum_char_2_3gram_overlap",
            "candidateOrdering": "ref_asc",
            "semanticInference": False,
            "sourceNetworkMutated": False,
        },
    }
    _assert_no_ranking_semantics(result)
    return copy.deepcopy(result)


def _assert_no_ranking_semantics(value: Any) -> None:
    if isinstance(value, dict):
        forbidden = FORBIDDEN_RANKING_KEYS & set(value)
        if forbidden:
            raise AssertionError(f"D1 emitted ranking semantics: {sorted(forbidden)}")
        for child in value.values():
            _assert_no_ranking_semantics(child)
    elif isinstance(value, list):
        for child in value:
            _assert_no_ranking_semantics(child)


def lexical_expand_from_snapshot(
    snapshot: dict[str, Any], anchor_refs: Iterable[str], **kwargs: Any
) -> dict[str, Any]:
    """Convenience boundary for a visibility-filtered formal snapshot."""

    try:
        network = D0Network(snapshot)
    except D0QueryError as exc:
        raise D1LexicalError(str(exc)) from exc
    return lexical_expand(network, anchor_refs, **kwargs)
