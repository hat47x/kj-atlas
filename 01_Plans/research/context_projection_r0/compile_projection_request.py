#!/usr/bin/env python3
"""Compile actor-aware research requests into the existing ContextQueryV1 shape.

Research-only. This module does not authorize callers, mutate graphs, or create
production contracts. Effective permissions must already be server-resolved.
"""

from __future__ import annotations

import json
from typing import Any

CONTEXT_QUERY_V1_KEYS = {
    "queryId",
    "goal",
    "scope",
    "depth",
    "constraints",
    "reviewFilter",
    "safeModePolicy",
    "outputMode",
    "previewConfirmed",
}

ACTOR_KINDS = {"human", "generative_ai", "sei_cognition", "external_system"}
ROLES = {
    "observe",
    "explore",
    "compare",
    "critique",
    "synthesize",
    "propose",
    "review",
    "approve",
    "publish",
}
INTENTS = {
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
PROJECTION_FORMS = {
    "subgraph",
    "path_list",
    "card_stack",
    "comparison_table",
    "spatial_layout",
    "timeline",
    "provenance_matrix",
    "compact_narrative",
}
SCOPES = {"document", "view", "island"}

_DEPTH_BY_INTENT = {
    "neighborhood": 1,
    "contrast": 2,
    "bridge": 4,
    "residual": 2,
    "unresolved": 2,
    "temporal": 2,
    "provenance": 2,
    "affinity": 2,
    "readout": 2,
}


class ProjectionCompileError(ValueError):
    pass


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProjectionCompileError(f"{field} must be a non-empty string")
    return value.strip()


def _string_list(value: Any, field: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ProjectionCompileError(f"{field} must be a list")
    result: list[str] = []
    for item in value:
        result.append(_require_string(item, field))
    return result


def _enum_list(value: Any, field: str, allowed: set[str]) -> list[str]:
    items = _string_list(value, field)
    unknown = sorted(set(items) - allowed)
    if unknown:
        raise ProjectionCompileError(f"{field} contains unknown values: {unknown}")
    return sorted(set(items))


def compile_projection_request(
    request: dict[str, Any], *, safe_mode_allows_unreviewed: bool = False
) -> dict[str, Any]:
    """Return a closed-world ContextQueryV1-shaped dict.

    `safe_mode_allows_unreviewed` is intentionally supplied by the trusted
    caller, not copied from the research request.
    """

    if not isinstance(request, dict):
        raise ProjectionCompileError("request must be an object")

    request_id = _require_string(request.get("requestId"), "requestId")
    inquiry = _require_string(request.get("inquiry"), "inquiry")

    actor = request.get("actor")
    if not isinstance(actor, dict):
        raise ProjectionCompileError("actor must be an object")
    actor_kind = _require_string(actor.get("kind"), "actor.kind")
    if actor_kind not in ACTOR_KINDS:
        raise ProjectionCompileError(f"unknown actor.kind: {actor_kind}")
    # actorRef is validated for traceability, but deliberately omitted from the
    # downstream ContextQuery to avoid turning identity into selection truth.
    _require_string(actor.get("actorRef"), "actor.actorRef")

    roles = _enum_list(request.get("roles"), "roles", ROLES)
    if not roles:
        raise ProjectionCompileError("roles must contain at least one role")

    source_scope = _require_string(request.get("sourceScope"), "sourceScope")
    if source_scope not in SCOPES:
        raise ProjectionCompileError(f"unknown sourceScope: {source_scope}")

    permission = request.get("permission")
    if not isinstance(permission, dict):
        raise ProjectionCompileError("permission must be an object")
    if permission.get("resolutionSource") != "server_resolved":
        raise ProjectionCompileError("permission must be server_resolved")

    readable_scopes = sorted(set(_string_list(permission.get("readableScopes"), "permission.readableScopes")))
    if not readable_scopes:
        raise ProjectionCompileError("permission.readableScopes must not be empty")

    for key in (
        "canSeeUnreviewed",
        "canCreateProposal",
        "canReview",
        "canApprove",
        "canPublish",
    ):
        if not isinstance(permission.get(key), bool):
            raise ProjectionCompileError(f"permission.{key} must be boolean")

    interest = request.get("interest", {})
    if not isinstance(interest, dict):
        raise ProjectionCompileError("interest must be an object")
    focus_refs = sorted(set(_string_list(interest.get("focusRefs"), "interest.focusRefs")))
    themes = sorted(set(_string_list(interest.get("themes"), "interest.themes")))
    intents = _enum_list(interest.get("seek"), "interest.seek", INTENTS)
    if not intents:
        intents = ["neighborhood"]

    desired_forms = _enum_list(
        request.get("desiredProjection"), "desiredProjection", PROJECTION_FORMS
    )

    diversity_need = request.get("diversityNeed", "default")
    unresolved_need = request.get("unresolvedNeed", "default")
    if diversity_need not in {"default", "increase"}:
        raise ProjectionCompileError("diversityNeed must be default or increase")
    if unresolved_need not in {"default", "increase"}:
        raise ProjectionCompileError("unresolvedNeed must be default or increase")

    preview_confirmed = request.get("previewConfirmed")
    if not isinstance(preview_confirmed, bool):
        raise ProjectionCompileError("previewConfirmed must be boolean")

    depth = min(5, max(_DEPTH_BY_INTENT[intent] for intent in intents))
    review_filter = (
        "includeUnreviewed"
        if permission["canSeeUnreviewed"] and safe_mode_allows_unreviewed
        else "reviewedOnly"
    )

    if "propose" in roles and permission["canCreateProposal"]:
        output_mode = "proposal"
    elif set(roles) & {"synthesize", "review", "approve", "publish"}:
        output_mode = "summary"
    else:
        output_mode = "candidate"

    goal = f"intents={','.join(intents)}; inquiry={inquiry}"
    constraints = {
        "projectionResearchR0": {
            "actorKind": actor_kind,
            "roles": roles,
            "focusRefs": focus_refs,
            "themes": themes,
            "intents": intents,
            "desiredProjection": desired_forms,
            "readableScopes": readable_scopes,
            "diversityNeed": diversity_need,
            "unresolvedNeed": unresolved_need,
        }
    }

    query = {
        "queryId": request_id,
        "goal": goal,
        "scope": source_scope,
        "depth": depth,
        "constraints": constraints,
        "reviewFilter": review_filter,
        "safeModePolicy": "strict",
        "outputMode": output_mode,
        "previewConfirmed": preview_confirmed,
    }

    if set(query) != CONTEXT_QUERY_V1_KEYS:
        raise AssertionError("compiler drifted from ContextQueryV1 top-level keys")
    return query


def canonical_json(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
