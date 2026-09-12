from __future__ import annotations

import copy
import json
from typing import Any


class ProjectionRequestError(ValueError):
    pass


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
SOURCE_SCOPES = {"network", "working", "consensus"}

TOP_LEVEL_KEYS = {
    "requestId",
    "actor",
    "roles",
    "interest",
    "inquiry",
    "permission",
    "sourceScope",
    "desiredProjection",
    "diversityNeed",
    "unresolvedNeed",
}
ACTOR_KEYS = {"actorRef", "kind"}
INTEREST_KEYS = {"focusRefs", "themes", "seek"}
PERMISSION_KEYS = {
    "resolutionSource",
    "readableScopes",
    "canSeeUnreviewed",
    "canCreateProposal",
    "canReview",
    "canApprove",
    "canPublish",
}


def _require_object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ProjectionRequestError(f"{field} must be an object")
    return value


def _closed_world(value: dict[str, Any], allowed: set[str], field: str) -> None:
    unknown = sorted(set(value) - allowed)
    missing = sorted(allowed - set(value))
    if unknown:
        raise ProjectionRequestError(f"{field} contains unknown keys: {unknown}")
    if missing:
        raise ProjectionRequestError(f"{field} is missing keys: {missing}")


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProjectionRequestError(f"{field} must be a non-empty string")
    return value.strip()


def _string_list(value: Any, field: str, *, allow_empty: bool = True) -> list[str]:
    if not isinstance(value, list):
        raise ProjectionRequestError(f"{field} must be a list")
    items = [_require_string(item, field) for item in value]
    normalized = sorted(set(items))
    if not allow_empty and not normalized:
        raise ProjectionRequestError(f"{field} must not be empty")
    return normalized


def _enum_list(value: Any, field: str, allowed: set[str], *, allow_empty: bool = True) -> list[str]:
    items = _string_list(value, field, allow_empty=allow_empty)
    unknown = sorted(set(items) - allowed)
    if unknown:
        raise ProjectionRequestError(f"{field} contains unknown values: {unknown}")
    return items


def normalize_projection_request(
    request: dict[str, Any], *, safe_mode_allows_unreviewed: bool = False
) -> tuple[dict[str, Any], str]:
    """Validate and normalize the formal ContextProjectionRequest.

    The request is consumed directly by the query pipeline. No legacy query
    contract is generated. SafeMode allowance is supplied by the trusted
    runtime rather than accepted from requester input.
    """

    request = _require_object(request, "request")
    _closed_world(request, TOP_LEVEL_KEYS, "request")

    actor = _require_object(request["actor"], "actor")
    _closed_world(actor, ACTOR_KEYS, "actor")
    actor_ref = _require_string(actor["actorRef"], "actor.actorRef")
    actor_kind = _require_string(actor["kind"], "actor.kind")
    if actor_kind not in ACTOR_KINDS:
        raise ProjectionRequestError(f"unknown actor.kind: {actor_kind}")

    roles = _enum_list(request["roles"], "roles", ROLES, allow_empty=False)

    interest = _require_object(request["interest"], "interest")
    _closed_world(interest, INTEREST_KEYS, "interest")
    focus_refs = _string_list(interest["focusRefs"], "interest.focusRefs")
    themes = _string_list(interest["themes"], "interest.themes")
    seek = _enum_list(
        interest["seek"], "interest.seek", QUERY_INTENTS, allow_empty=False
    )

    permission = _require_object(request["permission"], "permission")
    _closed_world(permission, PERMISSION_KEYS, "permission")
    if permission["resolutionSource"] != "server_resolved":
        raise ProjectionRequestError("permission must be server_resolved")
    readable_scopes = _string_list(
        permission["readableScopes"],
        "permission.readableScopes",
        allow_empty=False,
    )
    for key in (
        "canSeeUnreviewed",
        "canCreateProposal",
        "canReview",
        "canApprove",
        "canPublish",
    ):
        if not isinstance(permission[key], bool):
            raise ProjectionRequestError(f"permission.{key} must be boolean")

    source_scope = _require_string(request["sourceScope"], "sourceScope")
    if source_scope not in SOURCE_SCOPES:
        raise ProjectionRequestError(f"unknown sourceScope: {source_scope}")

    desired_projection = _enum_list(
        request["desiredProjection"],
        "desiredProjection",
        PROJECTION_FORMS,
    )

    diversity_need = _require_string(request["diversityNeed"], "diversityNeed")
    unresolved_need = _require_string(request["unresolvedNeed"], "unresolvedNeed")
    if diversity_need not in {"default", "increase"}:
        raise ProjectionRequestError("diversityNeed must be default or increase")
    if unresolved_need not in {"default", "increase"}:
        raise ProjectionRequestError("unresolvedNeed must be default or increase")

    normalized = {
        "requestId": _require_string(request["requestId"], "requestId"),
        "actor": {"actorRef": actor_ref, "kind": actor_kind},
        "roles": roles,
        "interest": {
            "focusRefs": focus_refs,
            "themes": themes,
            "seek": seek,
        },
        "inquiry": _require_string(request["inquiry"], "inquiry"),
        "permission": {
            "resolutionSource": "server_resolved",
            "readableScopes": readable_scopes,
            "canSeeUnreviewed": permission["canSeeUnreviewed"],
            "canCreateProposal": permission["canCreateProposal"],
            "canReview": permission["canReview"],
            "canApprove": permission["canApprove"],
            "canPublish": permission["canPublish"],
        },
        "sourceScope": source_scope,
        "desiredProjection": desired_projection,
        "diversityNeed": diversity_need,
        "unresolvedNeed": unresolved_need,
    }

    review_visibility = (
        "include_unreviewed"
        if permission["canSeeUnreviewed"] and safe_mode_allows_unreviewed
        else "reviewed_only"
    )
    return normalized, review_visibility


def canonical_json(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def selection_input_fingerprint(request: dict[str, Any]) -> dict[str, Any]:
    """Return actor-independent query inputs used to select content.

    Actor identity, role labels, and presentation preferences are intentionally
    excluded. Permission has already constrained the visible snapshot before
    selection.
    """

    return copy.deepcopy(
        {
            "interest": request["interest"],
            "inquiry": request["inquiry"],
            "sourceScope": request["sourceScope"],
            "diversityNeed": request["diversityNeed"],
            "unresolvedNeed": request["unresolvedNeed"],
        }
    )
