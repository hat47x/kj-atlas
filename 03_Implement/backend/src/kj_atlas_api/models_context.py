from __future__ import annotations

from hashlib import sha256
import json
from typing import Literal, Protocol

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

    schemaVersion: Literal["1.0.0"] = "1.0.0"
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

    schemaVersion: Literal["1.0.0"] = "1.0.0"
    bundleHash: str
    selected: list[dict[str, object]]
    relations: list[dict[str, object]]
    evidence: list[dict[str, object]]
    contradictions: list[dict[str, object]]
    reviewFlags: ReviewFlags
    truncationMeta: dict[str, object]
    excludedReason: list[str]
    queryCanonicalHash: str


class ContextBundleProvider(Protocol):
    def build_bundle(self, request: ContextBundleRequest) -> ContextBundleResponse: ...


class MockContextBundleProvider:
    def build_bundle(self, request: ContextBundleRequest) -> ContextBundleResponse:
        return build_bundle(request)


CONTEXT_BUNDLE_PROVIDER: ContextBundleProvider = MockContextBundleProvider()


class Ce4ResolveBundleRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=1)
    dryRun: bool
    sourceBundleHash: str = Field(pattern=r"^(sha256:[0-9a-f]{64}|mock:[0-9a-f]{64})$")
    safeMode: bool = True


class Ce4AuditChain(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str
    bundle: str
    proposal: str
    apply: str


class Ce4ResolveBundleResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schemaVersion: Literal["1.0.0"] = "1.0.0"
    equivalenceKey: str
    bundleHash: str
    queryCanonicalHash: str
    proposalLifecycle: Literal["proposed", "accepted", "rejected", "held"]
    sideEffect: str
    auditChain: Ce4AuditChain


_STUB_DATASET = {
    "selected": [
        {
            "id": "card-reviewed-01",
            "reviewed": True,
            "title": "Reviewed working hypothesis",
            "claimType": "hypothesis",
            "resolutionState": "unresolved",
            "aiDisposition": "constraint",
            "autoResolve": False,
        },
        {
            "id": "card-unreviewed-01",
            "reviewed": False,
            "title": "Unreviewed counter-opinion",
            "claimType": "unknown",
            "resolutionState": "unresolved",
            "aiDisposition": "constraint",
            "autoResolve": False,
        },
    ],
    "relations": [
        {
            "type": "supports",
            "from": "card-reviewed-01",
            "to": "card-unreviewed-01",
            "resolutionState": "unresolved",
            "aiDisposition": "constraint",
            "autoResolve": False,
        },
    ],
    "evidence": [
        {
            "cardId": "card-reviewed-01",
            "kind": "support",
            "reviewed": True,
            "resolutionState": "unresolved",
            "aiDisposition": "constraint",
            "autoResolve": False,
        },
        {
            "cardId": "card-unreviewed-01",
            "kind": "counter_opinion",
            "reviewed": False,
            "resolutionState": "unresolved",
            "aiDisposition": "constraint",
            "autoResolve": False,
        },
    ],
    "contradictions": [
        {
            "id": "ctr-01",
            "weight": 2,
            "label": "open conflict",
            "resolutionState": "unresolved",
            "aiDisposition": "constraint",
            "autoResolve": False,
        },
    ],
}

_HOLD_STATE_DATA_SOURCE = "hold:stub_dataset_contract_only"

# Stream C hold state: data-source integration is intentionally deferred until
# upstream schema/repository contracts are approved. Route/model I/F remains
# stable and deterministic against the frozen stub dataset contract.


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

    if query.safeModePolicy == "strict":
        before_count = len(selected)
        selected = [item for item in selected if item["reviewed"] is True]
        if len(selected) != before_count:
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
        truncationMeta={"stubDatasetId": request.stubDatasetId, "depth": query.depth, "holdState": _HOLD_STATE_DATA_SOURCE},
        excludedReason=sorted(excluded_reason),
        queryCanonicalHash=query_hash,
    )

    bundle_hash = _sha256_canonical(_canonical_bundle_hash_payload(provisional))
    return provisional.model_copy(update={"bundleHash": bundle_hash})


def build_ce4_resolved_bundle(request: Ce4ResolveBundleRequest) -> Ce4ResolveBundleResponse:
    if not request.safeMode:
        raise ValueError("safe_mode_required")

    query_canonical_hash = _sha256_canonical({"query": request.query.strip()})
    equivalence_key = _sha256_canonical(
        {
            "queryCanonicalHash": query_canonical_hash,
            "safeMode": request.safeMode,
        }
    )
    bundle_hash = _sha256_canonical(
        {
            "equivalenceKey": equivalence_key,
            "sourceBundleHash": request.sourceBundleHash,
        }
    )

    side_effect = "none" if request.dryRun else "write"
    if request.dryRun and side_effect != "none":
        raise ValueError("dry_run_requires_no_side_effect")

    return Ce4ResolveBundleResponse(
        equivalenceKey=equivalence_key,
        bundleHash=bundle_hash,
        queryCanonicalHash=query_canonical_hash,
        proposalLifecycle="proposed",
        sideEffect=side_effect,
        auditChain=Ce4AuditChain(
            query=f"query:{query_canonical_hash}",
            bundle=f"bundle:{bundle_hash}",
            proposal=f"proposal:{equivalence_key}",
            apply=f"apply:{equivalence_key}:{bundle_hash}",
        ),
    )
