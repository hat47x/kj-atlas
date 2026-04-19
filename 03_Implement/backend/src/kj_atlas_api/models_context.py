from __future__ import annotations

from hashlib import sha256
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ContextQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")

    queryId: str = Field(min_length=1)
    goal: str = Field(min_length=1)
    scope: Literal["document", "view", "island"]
    depth: int = Field(ge=0, le=5)
    constraints: dict[str, object]
    reviewFilter: Literal["reviewedOnly", "includeUnreviewed"]
    safeModePolicy: Literal["strict"]
    outputMode: Literal["summary", "proposal", "candidate"]
    previewConfirmed: bool = False


class ContextQueryValidationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    accepted: bool = True
    queryCanonicalHash: str


class ContextBundleRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: ContextQuery
    stubDatasetId: Literal["A2-minimal-v1"]


class ReviewFlags(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reviewed: int
    unreviewed: int


class ContextBundleResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    bundleHash: str
    selected: list[dict[str, object]]
    relations: list[dict[str, object]]
    evidence: list[dict[str, object]]
    contradictions: list[dict[str, object]]
    reviewFlags: ReviewFlags
    truncationMeta: dict[str, object]
    excludedReason: list[str]
    queryCanonicalHash: str


_STUB_DATASET = {
    "selected": [
        {"id": "card-reviewed-01", "reviewed": True, "title": "Reviewed card"},
        {"id": "card-unreviewed-01", "reviewed": False, "title": "Unreviewed card"},
    ],
    "relations": [
        {"type": "supports", "from": "card-reviewed-01", "to": "card-unreviewed-01"},
    ],
    "evidence": [
        {"cardId": "card-reviewed-01", "kind": "note"},
        {"cardId": "card-unreviewed-01", "kind": "note"},
    ],
    "contradictions": [
        {"id": "ctr-01", "weight": 2, "label": "open conflict"},
    ],
}


def _stable_value(value: object) -> object:
    if isinstance(value, dict):
        return {key: _stable_value(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [_stable_value(item) for item in value]
    return value


def _canonical_query_hash_payload(query: ContextQuery) -> dict[str, object]:
    return {
        "queryId": query.queryId,
        "goal": query.goal,
        "scope": query.scope,
        "depth": query.depth,
        "constraints": _stable_value(query.constraints),
        "reviewFilter": query.reviewFilter,
        "safeModePolicy": query.safeModePolicy,
        "outputMode": query.outputMode,
        "previewConfirmed": query.previewConfirmed,
    }


def _canonical_bundle_hash_payload(bundle: ContextBundleResponse) -> dict[str, object]:
    return {
        "selected": sorted((_stable_value(item) for item in bundle.selected), key=lambda item: item["id"]),
        "relations": sorted(
            (_stable_value(item) for item in bundle.relations),
            key=lambda item: (item["type"], item["from"], item["to"]),
        ),
        "evidence": sorted((_stable_value(item) for item in bundle.evidence), key=lambda item: item["cardId"]),
        "contradictions": sorted(
            (_stable_value(item) for item in bundle.contradictions),
            key=lambda item: (-int(item["weight"]), item["id"]),
        ),
        "reviewFlags": bundle.reviewFlags.model_dump(mode="json"),
        "truncationMeta": _stable_value(bundle.truncationMeta),
        "excludedReason": sorted(bundle.excludedReason),
    }


def _sha256_canonical(payload: dict[str, object]) -> str:
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()


def build_bundle(request: ContextBundleRequest) -> ContextBundleResponse:
    query = request.query
    if not query.previewConfirmed:
        raise ValueError("preview_required")

    query_hash = _sha256_canonical(_canonical_query_hash_payload(query))

    selected = sorted(_STUB_DATASET["selected"], key=lambda item: item["id"])
    excluded_reason: list[str] = []

    if query.reviewFilter == "reviewedOnly":
        selected = [item for item in selected if item["reviewed"] is True]
        excluded_reason.append("unreviewed_filtered")

    if query.safeModePolicy == "strict" and query.reviewFilter == "includeUnreviewed":
        excluded_reason.append("safe_mode_unreviewed_text")

    relations = sorted(_STUB_DATASET["relations"], key=lambda item: (item["type"], item["from"], item["to"]))
    evidence = sorted(_STUB_DATASET["evidence"], key=lambda item: item["cardId"])
    contradictions = sorted(_STUB_DATASET["contradictions"], key=lambda item: (-item["weight"], item["id"]))

    review_flags = ReviewFlags(
        reviewed=sum(1 for item in selected if item["reviewed"] is True),
        unreviewed=sum(1 for item in selected if item["reviewed"] is False),
    )

    provisional = ContextBundleResponse(
        bundleHash="",
        selected=selected,
        relations=relations,
        evidence=evidence,
        contradictions=contradictions,
        reviewFlags=review_flags,
        truncationMeta={"stubDatasetId": request.stubDatasetId, "depth": query.depth},
        excludedReason=sorted(excluded_reason),
        queryCanonicalHash=query_hash,
    )

    bundle_hash = _sha256_canonical(_canonical_bundle_hash_payload(provisional))
    return provisional.model_copy(update={"bundleHash": bundle_hash})
