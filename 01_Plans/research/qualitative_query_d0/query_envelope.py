#!/usr/bin/env python3
"""Multi-channel query envelope for SUI Information Network research.

The envelope preserves one deterministic D0 Selection as the only selected
content. D1/D2 candidate channels remain supplemental observations and are never
promoted into Selection by composition. Cross-channel presence is descriptive,
not a vote, confidence, score, rank, or consensus signal.
"""

from __future__ import annotations

import copy
from collections import defaultdict
from typing import Any, Iterable

from query_engine import D0Network


class QueryEnvelopeError(ValueError):
    pass


SCHEMA = "sui.multi-channel-query-envelope/v1alpha1"
_ALLOWED_CHANNELS = {"lexical_sparse", "associative_sparse"}
_FORBIDDEN_RANKING_KEYS = {
    "score",
    "confidence",
    "importance",
    "rank",
    "activation",
    "similarity",
    "novelty_signal",
}


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise QueryEnvelopeError(f"{field} must be a non-empty string")
    return value.strip()


def _require_ref_list(value: Any, field: str, known_refs: set[str]) -> list[str]:
    if not isinstance(value, list):
        raise QueryEnvelopeError(f"{field} must be a list")
    refs = [_require_string(item, field) for item in value]
    if len(refs) != len(set(refs)):
        raise QueryEnvelopeError(f"{field} must not contain duplicates")
    unknown = sorted(set(refs) - known_refs)
    if unknown:
        raise QueryEnvelopeError(f"{field} contains refs outside snapshot: {unknown}")
    return refs


def _assert_no_ranking_signals(value: Any, path: str = "root") -> None:
    if isinstance(value, dict):
        forbidden = _FORBIDDEN_RANKING_KEYS & set(value)
        if forbidden:
            raise QueryEnvelopeError(
                f"{path} contains forbidden ranking/provider signals: {sorted(forbidden)}"
            )
        for key, child in value.items():
            _assert_no_ranking_signals(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _assert_no_ranking_signals(child, f"{path}[{index}]")


def _normalize_deterministic_selection(
    network: D0Network, intent: str, selection: dict[str, Any]
) -> dict[str, Any]:
    if not isinstance(selection, dict):
        raise QueryEnvelopeError("deterministicSelection must be an object")
    _assert_no_ranking_signals(selection, "deterministicSelection")
    if selection.get("intent") != intent:
        raise QueryEnvelopeError("deterministicSelection.intent must match envelope intent")
    trace = selection.get("trace")
    if not isinstance(trace, dict) or trace.get("networkId") != network.network_id:
        raise QueryEnvelopeError("deterministicSelection must belong to the same network")

    known_nodes = set(network.nodes)
    known_edges = set(network.edges)
    selected_nodes = _require_ref_list(
        selection.get("selectedNodeRefs"), "deterministicSelection.selectedNodeRefs", known_nodes
    )
    selected_edges = _require_ref_list(
        selection.get("selectedEdgeRefs"), "deterministicSelection.selectedEdgeRefs", known_edges
    )

    normalized = copy.deepcopy(selection)
    normalized["selectedNodeRefs"] = sorted(selected_nodes)
    normalized["selectedEdgeRefs"] = sorted(selected_edges)
    return normalized


def _normalize_candidate_channel(
    network: D0Network, channel: dict[str, Any]
) -> dict[str, Any]:
    if not isinstance(channel, dict):
        raise QueryEnvelopeError("candidate channel must be an object")
    _assert_no_ranking_signals(channel, "candidateChannel")

    channel_name = channel.get("channel")
    if channel_name not in _ALLOWED_CHANNELS:
        raise QueryEnvelopeError(f"unsupported candidate channel: {channel_name}")
    trace = channel.get("trace")
    if not isinstance(trace, dict) or trace.get("networkId") != network.network_id:
        raise QueryEnvelopeError("candidate channel must belong to the same network")

    known_nodes = set(network.nodes)
    anchor_refs = _require_ref_list(channel.get("anchorRefs"), "anchorRefs", known_nodes)
    candidate_refs = _require_ref_list(channel.get("candidateRefs"), "candidateRefs", known_nodes)
    if set(anchor_refs) & set(candidate_refs):
        raise QueryEnvelopeError("candidate channel must not return its anchor as a candidate")

    normalized = copy.deepcopy(channel)
    normalized["anchorRefs"] = sorted(anchor_refs)
    normalized["candidateRefs"] = sorted(candidate_refs)
    return normalized


def _channel_presence(channels: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    presence: dict[str, set[str]] = defaultdict(set)
    for channel in channels:
        for ref in channel["candidateRefs"]:
            presence[ref].add(channel["channel"])
    return [
        {"ref": ref, "channels": sorted(channel_names)}
        for ref, channel_names in sorted(presence.items())
    ]


def compose_query_envelope(
    network: D0Network,
    *,
    request_id: str,
    intent: str,
    deterministic_selection: dict[str, Any],
    candidate_channels: Iterable[dict[str, Any]] = (),
) -> dict[str, Any]:
    """Compose D0 and supplemental candidate channels without promotion.

    `deterministicSelection.selectedNodeRefs` is copied as-is (stable-sorted)
    and is never expanded from D1/D2 candidate refs. `channelPresence` exists
    only to expose which independent channels mentioned a ref.
    """

    request_id = _require_string(request_id, "requestId")
    intent = _require_string(intent, "intent")
    selection = _normalize_deterministic_selection(network, intent, deterministic_selection)

    normalized_channels = [
        _normalize_candidate_channel(network, channel) for channel in candidate_channels
    ]
    names = [channel["channel"] for channel in normalized_channels]
    if len(names) != len(set(names)):
        raise QueryEnvelopeError("candidate channel names must be unique")
    normalized_channels.sort(key=lambda channel: channel["channel"])

    selection_node_refs = list(selection["selectedNodeRefs"])
    result = {
        "schema": SCHEMA,
        "requestId": request_id,
        "networkId": network.network_id,
        "intent": intent,
        "deterministicSelection": selection,
        "candidateChannels": normalized_channels,
        "channelPresence": _channel_presence(normalized_channels),
        "trace": {
            "selectionAuthority": "d0_deterministic_only",
            "candidateAutoPromotion": False,
            "compositeRanking": False,
            "crossChannelPresenceIsVote": False,
            "sourceNetworkMutated": False,
        },
    }

    if result["deterministicSelection"]["selectedNodeRefs"] != selection_node_refs:
        raise AssertionError("candidate composition mutated deterministic selection")
    _assert_no_ranking_signals(result)
    return copy.deepcopy(result)
