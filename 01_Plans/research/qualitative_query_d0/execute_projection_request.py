#!/usr/bin/env python3
"""End-to-end research adapter: ProjectionRequestR0 -> D0 selection -> projections.

The adapter assumes authorization has already produced effective permissions.
It applies the compiled reviewFilter before D0 selection. It does not infer
intent parameters from natural-language inquiry beyond explicit R0 fields.
"""

from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
CONTEXT_R0 = HERE.parent / "context_projection_r0"
if str(CONTEXT_R0) not in sys.path:
    sys.path.insert(0, str(CONTEXT_R0))

from compile_projection_request import canonical_json, compile_projection_request  # noqa: E402
from projection import D0ProjectionError, project  # noqa: E402
from query_engine import D0Network, D0QueryError  # noqa: E402


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


def _filter_network_for_review(data: dict[str, Any], review_filter: str) -> dict[str, Any]:
    if review_filter == "includeUnreviewed":
        return copy.deepcopy(data)
    if review_filter != "reviewedOnly":
        raise D0ExecutionError(f"unsupported reviewFilter: {review_filter}")

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
    interest = request.get("interest", {})
    seek = interest.get("seek", []) if isinstance(interest, dict) else []
    supported = sorted(set(seek) & D0_SELECTION_INTENTS)
    unsupported = sorted(set(seek) - D0_SELECTION_INTENTS - {"readout", "affinity"})
    if unsupported:
        raise D0ExecutionError(f"unknown D0 intents: {unsupported}")
    if len(supported) != 1:
        raise D0ExecutionError(
            "first D0 end-to-end slice requires exactly one deterministic selection intent"
        )
    return supported[0]


def _execute_selection(network: D0Network, request: dict[str, Any], intent: str) -> dict[str, Any]:
    interest = request.get("interest", {})
    focus = sorted(set(interest.get("focusRefs", [])))

    if intent == "neighborhood":
        if not focus:
            raise D0ExecutionError("neighborhood requires focusRefs")
        return network.neighborhood(focus, depth=1)
    if intent == "contrast":
        if len(focus) != 2:
            raise D0ExecutionError("contrast first slice requires exactly two focusRefs")
        return network.contrast([focus[0]], [focus[1]])
    if intent == "bridge":
        if len(focus) != 2:
            raise D0ExecutionError("bridge first slice requires exactly two focusRefs")
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
    compiled = compile_projection_request(
        request, safe_mode_allows_unreviewed=safe_mode_allows_unreviewed
    )
    filtered_data = _filter_network_for_review(network_data, compiled["reviewFilter"])
    network = D0Network(filtered_data)
    intent = _choose_intent(request)

    try:
        selection = _execute_selection(network, request, intent)
    except D0QueryError as exc:
        raise D0ExecutionError(str(exc)) from exc

    projections: list[dict[str, Any]] = []
    deferred: list[dict[str, str]] = []
    for form in sorted(set(request.get("desiredProjection", []))):
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

    actor = request.get("actor", {})
    return {
        "requestId": request.get("requestId"),
        "actorRef": actor.get("actorRef"),
        "actorKind": actor.get("kind"),
        "compiledContextQuery": compiled,
        "selection": selection,
        "selectionDigest": _digest(selection),
        "projections": projections,
        "deferredProjectionForms": deferred,
        "trace": {
            "networkId": filtered_data.get("networkId"),
            "reviewFilter": compiled["reviewFilter"],
            "selectionTier": "D0",
            "sourceNetworkMutated": False,
        },
    }
