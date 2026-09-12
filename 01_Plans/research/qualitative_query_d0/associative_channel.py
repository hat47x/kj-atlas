#!/usr/bin/env python3
"""Provider-neutral D2 associative cognition boundary for SUI query snapshots.

This adapter owns feature meaning and response validation. It intentionally does
not import or depend on a concrete SEI/SACS implementation. Provider activation,
similarity, confidence, and rank are not part of the SUI boundary.
"""

from __future__ import annotations

import copy
from typing import Any, Iterable

from query_engine import D0Network


class D2AssociativeError(ValueError):
    pass


REQUEST_SCHEMA = "sui.associative-recall-request/v1alpha1"
RESPONSE_SCHEMA = "sui.associative-recall-response/v1alpha1"
QUERY_INTENTS = {
    "neighborhood",
    "contrast",
    "bridge",
    "residual",
    "unresolved",
    "temporal",
    "provenance",
    "affinity",
    "readout",
}
FORBIDDEN_SIGNAL_KEYS = {
    "score",
    "confidence",
    "importance",
    "rank",
    "activation",
    "similarity",
    "novelty_signal",
}
_RESPONSE_KEYS = {
    "schema",
    "requestId",
    "provider",
    "outcome",
    "candidateRefs",
    "evidence",
    "noveltyCue",
}
_PROVIDER_KEYS = {"providerId", "implementationVersion"}
_EVIDENCE_KEYS = {"ref", "matchedChannelRefs"}


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise D2AssociativeError(f"{field} must be a non-empty string")
    return value.strip()


def _require_string_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list):
        raise D2AssociativeError(f"{field} must be a list")
    result = [_require_string(item, field) for item in value]
    if len(result) != len(set(result)):
        raise D2AssociativeError(f"{field} must not contain duplicates")
    return result


def _node_channel_refs(item: dict[str, Any]) -> set[str]:
    """Return externally explainable channel provenance refs.

    These refs only establish that a channel/attribute exists on an item. They
    do not prove semantic equivalence or reconstruct provider activation.
    """

    channels = item.get("channels", {})
    refs: set[str] = set()
    if isinstance(channels.get("text"), str) and channels["text"].strip():
        refs.add("channel:text")
    graph = channels.get("graph")
    if isinstance(graph, dict):
        refs.update(f"graph:relationType:{value}" for value in graph.get("relationTypes", []))
        refs.update(f"graph:neighborKind:{value}" for value in graph.get("neighborKinds", []))
    provenance = channels.get("provenance")
    if isinstance(provenance, dict):
        refs.update(f"provenance:source:{value}" for value in provenance.get("sourceRefs", []))
        refs.update(f"provenance:actor:{value}" for value in provenance.get("actorRefs", []))
    grouping = channels.get("grouping")
    if isinstance(grouping, dict):
        island_ref = grouping.get("islandRef")
        hold_state = grouping.get("holdState")
        if isinstance(island_ref, str) and island_ref:
            refs.add(f"grouping:island:{island_ref}")
        if isinstance(hold_state, str) and hold_state:
            refs.add(f"grouping:hold:{hold_state}")
    return refs


def _channels_for_node(network: D0Network, ref: str) -> dict[str, Any]:
    node = network.nodes[ref]
    channels: dict[str, Any] = {}

    text = node.get("text")
    if isinstance(text, str) and text.strip():
        channels["text"] = text

    relation_types: set[str] = set()
    neighbor_kinds: set[str] = set()
    for edge in network.edges.values():
        other: str | None = None
        if edge["fromId"] == ref:
            other = edge["toId"]
        elif edge["toId"] == ref:
            other = edge["fromId"]
        if other is None:
            continue
        relation_type = edge.get("type")
        if isinstance(relation_type, str) and relation_type:
            relation_types.add(relation_type)
        other_kind = network.nodes[other].get("kind")
        if isinstance(other_kind, str) and other_kind:
            neighbor_kinds.add(other_kind)
    if relation_types or neighbor_kinds:
        channels["graph"] = {
            "relationTypes": sorted(relation_types),
            "neighborKinds": sorted(neighbor_kinds),
        }

    source_refs = sorted(set(node.get("sourceRefs", [])))
    actor_refs = sorted(set(node.get("actorRefs", [])))
    if source_refs or actor_refs:
        channels["provenance"] = {
            "sourceRefs": source_refs,
            "actorRefs": actor_refs,
        }

    grouping: dict[str, str] = {}
    island_ref = node.get("islandId")
    hold_state = node.get("holdState")
    if isinstance(island_ref, str) and island_ref:
        grouping["islandRef"] = island_ref
    if isinstance(hold_state, str) and hold_state:
        grouping["holdState"] = hold_state
    if grouping:
        channels["grouping"] = grouping

    return channels


def build_associative_request(
    network: D0Network,
    *,
    request_id: str,
    intent: str,
    anchor_refs: Iterable[str],
    scope_refs: Iterable[str] | None = None,
    candidate_limit: int = 8,
) -> dict[str, Any]:
    request_id = _require_string(request_id, "requestId")
    if intent not in QUERY_INTENTS:
        raise D2AssociativeError(f"unknown intent: {intent}")
    anchors = sorted(set(anchor_refs))
    if not anchors:
        raise D2AssociativeError("anchorRefs must not be empty")
    unknown_anchors = [ref for ref in anchors if ref not in network.nodes]
    if unknown_anchors:
        raise D2AssociativeError(f"anchorRefs contains unknown refs: {unknown_anchors}")
    if not isinstance(candidate_limit, int) or candidate_limit < 1:
        raise D2AssociativeError("candidateLimit must be a positive integer")

    scope = sorted(network.nodes) if scope_refs is None else sorted(set(scope_refs))
    if not scope:
        raise D2AssociativeError("scopeRefs must not be empty")
    unknown_scope = [ref for ref in scope if ref not in network.nodes]
    if unknown_scope:
        raise D2AssociativeError(f"scopeRefs contains unknown refs: {unknown_scope}")
    if not set(anchors).issubset(scope):
        raise D2AssociativeError("anchorRefs must be contained in scopeRefs")

    items = [
        {
            "ref": ref,
            "kind": _require_string(network.nodes[ref].get("kind"), f"node[{ref}].kind"),
            "channels": _channels_for_node(network, ref),
        }
        for ref in scope
    ]
    return {
        "schema": REQUEST_SCHEMA,
        "requestId": request_id,
        "networkId": network.network_id,
        "intent": intent,
        "anchorRefs": anchors,
        "items": items,
        "policy": {"candidateLimit": candidate_limit},
    }


def _assert_no_forbidden_signals(value: Any) -> None:
    if isinstance(value, dict):
        forbidden = FORBIDDEN_SIGNAL_KEYS & set(value)
        if forbidden:
            raise D2AssociativeError(
                f"provider response leaked forbidden signals: {sorted(forbidden)}"
            )
        for child in value.values():
            _assert_no_forbidden_signals(child)
    elif isinstance(value, list):
        for child in value:
            _assert_no_forbidden_signals(child)


def normalize_associative_response(
    request: dict[str, Any], response: dict[str, Any]
) -> dict[str, Any]:
    if not isinstance(response, dict):
        raise D2AssociativeError("response must be an object")
    unknown = sorted(set(response) - _RESPONSE_KEYS)
    missing = sorted(_RESPONSE_KEYS - set(response))
    if unknown:
        raise D2AssociativeError(f"response contains unknown keys: {unknown}")
    if missing:
        raise D2AssociativeError(f"response is missing keys: {missing}")
    _assert_no_forbidden_signals(response)

    if response["schema"] != RESPONSE_SCHEMA:
        raise D2AssociativeError("unsupported response schema")
    if response["requestId"] != request["requestId"]:
        raise D2AssociativeError("response requestId mismatch")

    provider = response["provider"]
    if not isinstance(provider, dict) or set(provider) != _PROVIDER_KEYS:
        raise D2AssociativeError("provider must contain exactly providerId and implementationVersion")
    provider_id = _require_string(provider["providerId"], "provider.providerId")
    implementation_version = _require_string(
        provider["implementationVersion"], "provider.implementationVersion"
    )

    outcome = response["outcome"]
    if outcome not in {"candidates", "abstain"}:
        raise D2AssociativeError("outcome must be candidates or abstain")
    novelty_cue = response["noveltyCue"]
    if novelty_cue not in {"none", "abstain"}:
        raise D2AssociativeError("noveltyCue must be none or abstain")

    candidate_refs = _require_string_list(response["candidateRefs"], "candidateRefs")
    item_by_ref = {item["ref"]: item for item in request["items"]}
    anchors = set(request["anchorRefs"])
    unknown_candidates = [ref for ref in candidate_refs if ref not in item_by_ref]
    if unknown_candidates:
        raise D2AssociativeError(f"candidateRefs outside request scope: {unknown_candidates}")
    if anchors & set(candidate_refs):
        raise D2AssociativeError("anchorRefs must not be returned as candidates")
    if len(candidate_refs) > request["policy"]["candidateLimit"]:
        raise D2AssociativeError("candidateRefs exceeds candidateLimit")

    if outcome == "abstain":
        if candidate_refs or novelty_cue != "abstain":
            raise D2AssociativeError("abstain requires empty candidates and noveltyCue=abstain")
    elif novelty_cue != "none":
        raise D2AssociativeError("candidate outcome requires noveltyCue=none")

    evidence_value = response["evidence"]
    if not isinstance(evidence_value, list):
        raise D2AssociativeError("evidence must be a list")
    evidence_by_ref: dict[str, list[str]] = {}
    anchor_channel_refs: set[str] = set()
    for anchor_ref in anchors:
        anchor_channel_refs.update(_node_channel_refs(item_by_ref[anchor_ref]))

    for evidence in evidence_value:
        if not isinstance(evidence, dict) or set(evidence) != _EVIDENCE_KEYS:
            raise D2AssociativeError("evidence item must contain exactly ref and matchedChannelRefs")
        ref = _require_string(evidence["ref"], "evidence.ref")
        if ref not in candidate_refs:
            raise D2AssociativeError("evidence.ref must be a candidateRef")
        if ref in evidence_by_ref:
            raise D2AssociativeError("duplicate evidence.ref")
        matched = _require_string_list(evidence["matchedChannelRefs"], "matchedChannelRefs")
        allowed = _node_channel_refs(item_by_ref[ref]) & anchor_channel_refs
        invented = sorted(set(matched) - allowed)
        if invented:
            raise D2AssociativeError(
                f"matchedChannelRefs not present on both anchor and candidate: {invented}"
            )
        evidence_by_ref[ref] = sorted(matched)

    normalized_candidates = sorted(candidate_refs)
    return {
        "channel": "associative_sparse",
        "anchorRefs": sorted(anchors),
        "candidateRefs": normalized_candidates,
        "items": [
            {
                "ref": ref,
                "evidence": {"matchedChannelRefs": evidence_by_ref.get(ref, [])},
            }
            for ref in normalized_candidates
        ],
        "noveltyCue": novelty_cue,
        "trace": {
            "networkId": request["networkId"],
            "providerId": provider_id,
            "implementationVersion": implementation_version,
            "semanticAuthority": False,
            "sourceNetworkMutated": False,
        },
    }


def build_and_normalize_associative_channel(
    network: D0Network,
    response: dict[str, Any],
    **request_kwargs: Any,
) -> dict[str, Any]:
    request = build_associative_request(network, **request_kwargs)
    return copy.deepcopy(normalize_associative_response(request, response))
