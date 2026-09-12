#!/usr/bin/env python3
"""Formal ContextProjectionRequest -> D0 selection -> actor-facing projection.

The pipeline consumes the formal request directly. Authorization is assumed to
have produced effective permissions before entry. SafeMode is a trusted runtime
input. No legacy Document/ContextQuery compatibility object is generated.
"""

from __future__ import annotations

import copy
import hashlib
from typing import Any

from projection import D0ProjectionError, project
from projection_request import (
    ProjectionRequestError,
    canonical_json,
    normalize_projection_request,
)
from query_engine import D0Network, D0QueryError


class D0ExecutionError(ValueError):
    pass


D0_SELECTION_INTENTS = {
    "neighborhood",
    "contrast",
    "bridge",
    "residual",
    "unresolved",
    "temporal",
    "provenance",
}


def _filter_network_for_review(data: dict[str, Any], review_visibility: str) -> dict[str, Any]:
    if review_visibility == "include_unreviewed":
        return copy.deepcopy(data)
    if review_visibility != "reviewed_only":
        raise D0ExecutionError(f"unsupported review visibility: {review_visibility}")

    visible_nodes = {
        node["id"]
        for node in data.get("nodes", [])
        if node.get("reviewState") == "human_reviewed"
    }
    filtered = copy.deepcopy(data)
    filtered["nodes"] = [node for node in filtered.get("nodes", []) if node["id"] in visible_nodes]
    filtered["edges"] = [
        edge
        for edge in filtered.get("edges", [])
        if edge["fromId"] in visible_nodes and edge["toId"] in visible_nodes
    ]
    filtered["critiques"] = [
        item for item in filtered.get("critiques", []) if item["targetRef"] in visible_nodes
    ]
    filtered["contradictions"] = [
        item
        for item in filtered.get("contradictions", [])
        if item["fromId"] in visible_nodes and item["toId"] in visible_nodes
    ]
    filtered["events"] = [
        item
        for item in filtered.get("events", [])
        if set(item.get("targetRefs", [])).issubset(visible_nodes)
    ]
    referenced_sources = {
        source_ref
        for node in filtered["nodes"]
        for source_ref in node.get("sourceRefs", [])
    }
    filtered["sources"] = [
        source for source in filtered.get("sources", []) if source["id"] in referenced_sources
    ]
    return filtered


def _choose_intent(request: dict[str, Any]) -> str:
    seek = request["interest"]["seek"]
    supported = sorted(set(seek) & D0_SELECTION_INTENTS)
    unsupported = sorted(set(seek) - D0_SELECTION_INTENTS - {"readout", "affinity"})
    if unsupported:
        raise D0ExecutionError(f"unknown D0 intents: {unsupported}")
    if len(supported) != 1:
        raise D0ExecutionError(
            "D0 requires exactly one deterministic selection intent; "
            "affinity/readout are handled by later tiers"
        )
    return supported[0]


def _execute_selection(network: D0Network, request: dict[str, Any], intent: str) -> dict[str, Any]:
    focus = request["interest"]["focusRefs"]

    if intent == "neighborhood":
        if not focus:
            raise D0ExecutionError("neighborhood requires focusRefs")
        return network.neighborhood(focus, depth=1)
    if intent == "contrast":
        if len(focus) != 2:
            raise D0ExecutionError("contrast D0 slice requires exactly two focusRefs")
        return network.contrast([focus[0]], [focus[1]])
    if intent == "bridge":
        if len(focus) != 2:
            raise D0ExecutionError("bridge D0 slice requires exactly two focusRefs")
        return network.bridge(focus[0], focus[1])
    if intent == "residual":
        return network.residual(focus or None)
    if intent == "unresolved":
        return network.unresolved(focus or None)
    if intent == "temporal":
        return network.temporal(focus or None)
    if intent == "provenance":
        return network.provenance(focus or None)
    raise AssertionError("unreachable D0 intent")


def _digest(value: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def execute_projection_request(
    network_data: dict[str, Any],
    request: dict[str, Any],
    *,
    safe_mode_allows_unreviewed: bool = False,
) -> dict[str, Any]:
    try:
        normalized, review_visibility = normalize_projection_request(
            request,
            safe_mode_allows_unreviewed=safe_mode_allows_unreviewed,
        )
    except ProjectionRequestError as exc:
        raise D0ExecutionError(str(exc)) from exc

    filtered_data = _filter_network_for_review(network_data, review_visibility)
    network = D0Network(filtered_data)
    intent = _choose_intent(normalized)

    try:
        selection = _execute_selection(network, normalized, intent)
    except D0QueryError as exc:
        raise D0ExecutionError(str(exc)) from exc

    projections: list[dict[str, Any]] = []
    deferred: list[dict[str, str]] = []
    for form in normalized["desiredProjection"]:
        if form == "compact_narrative":
            deferred.append(
                {
                    "form": form,
                    "tier": "D4",
                    "reason": "generated narrative is outside deterministic D0",
                }
            )
            continue
        try:
            projections.append(project(network, selection, form))
        except D0ProjectionError as exc:
            raise D0ExecutionError(str(exc)) from exc

    return {
        "requestId": normalized["requestId"],
        "actor": normalized["actor"],
        "selection": selection,
        "selectionDigest": _digest(selection),
        "projections": projections,
        "deferredProjectionForms": deferred,
        "trace": {
            "networkId": filtered_data.get("networkId"),
            "sourceScope": normalized["sourceScope"],
            "readableScopes": normalized["permission"]["readableScopes"],
            "reviewVisibility": review_visibility,
            "selectionTier": "D0",
            "sourceNetworkMutated": False,
        },
    }
