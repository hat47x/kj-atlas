from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from kj_atlas_api.models import DocumentV1


SOURCE_BUNDLE_HASH_PATTERN = r"^(?:[0-9a-f]{64}|mock:[0-9a-f]{64})$"


class ProviderStatusResponse(BaseModel):
    """PROV-VIS-01 (ADR-0050 D1): read-only echo of the configured LLM
    provider kind. This is NOT a live connectivity check — it reports the
    resolved provider_kind only. "fixture" is a test-only provider selected
    directly in Python tests, never via KJ_ATLAS_LLM_PROVIDER, so it is not a
    reachable runtime value here."""

    model_config = ConfigDict(extra="forbid")

    providerKind: Literal["none", "local", "large-scale"]


class NarrativeIssueReference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    kind: Literal["card", "island"]


class NarrativeIssue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    severity: Literal["info", "warn", "error"]
    message: str = Field(min_length=1)
    references: list[NarrativeIssueReference] | None = None


class CheckNarrativeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    doc: DocumentV1
    narrativeText: str = Field(min_length=1)
    basedOnReadingOrder: list[str] | None = None


class CheckNarrativeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    issues: list[NarrativeIssue]


class GenerateNarrativeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    doc: DocumentV1
    narrativeTitle: str | None = None


class GenerateNarrativeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str
    basedOnReadingOrder: list[str]
    warnings: list[str] | None = None


class SuggestIslandSummaryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    doc: DocumentV1
    islandId: str = Field(min_length=1)


class SuggestIslandSummaryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summaryText: str = Field(min_length=1)
    groundingIds: list[str] = Field(min_length=1)
    warnings: list[str] | None = None


class RelationEdgeText(BaseModel):
    model_config = ConfigDict(extra="forbid")

    edgeId: str = Field(min_length=1)
    type: str = Field(min_length=1)
    from_: str = Field(min_length=1, alias="from")
    to: str = Field(min_length=1)


class RelationCardText(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    text: str = Field(min_length=1)


class SummarizeIslandRelationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    doc: DocumentV1
    islandAId: str = Field(min_length=1)
    islandBId: str = Field(min_length=1)
    relationType: Literal["related", "negate", "causal", "mutual", "equivalence", "unknown"]
    derived: bool
    groundingCardIds: list[str]
    groundingEdgeIds: list[str]
    edgeTexts: list[RelationEdgeText] | None = None
    cardTexts: list[RelationCardText]


class SummarizeIslandRelationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1)
    groundingCardIds: list[str]
    groundingEdgeIds: list[str]
    warnings: list[str]


class ProposalDiff(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entityType: Literal["island_summary"]
    targetId: str = Field(min_length=1)
    field: Literal["summaryText"]
    before: str | None = None
    after: str = Field(min_length=1)
    groundingIds: list[str] = Field(min_length=1)
    warnings: list[str] | None = None


class ProposalEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    proposalId: str = Field(min_length=1)
    type: Literal["island_summary"]
    status: Literal["proposed", "accepted", "rejected", "held"]
    reviewState: Literal["unreviewed"] = "unreviewed"
    sourceBundleHash: str = Field(pattern=SOURCE_BUNDLE_HASH_PATTERN)
    diff: ProposalDiff
    rationale: str = Field(min_length=1)


class ProposeIslandSummaryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    doc: DocumentV1
    islandId: str = Field(min_length=1)
    sourceBundleHash: str = Field(pattern=SOURCE_BUNDLE_HASH_PATTERN)


class ProposalDecisionAuditRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    proposalId: str = Field(min_length=1)
    decision: Literal["accepted", "rejected", "held", "adopt", "reject", "hold"]
    actor: str = Field(min_length=1)
    reason: str | None = None


class ProposalDecisionAuditResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    proposalId: str = Field(min_length=1)
    status: Literal["accepted", "rejected", "held"]
    reviewState: Literal["unreviewed"]
    recordedAt: str = Field(min_length=1)


# ---------------------------------------------------------------------------
# ADR-0064: KJ-method card-level AI operations
# ---------------------------------------------------------------------------


class RefineCardTextRequest(BaseModel):
    """Request to refine/improve the wording of a single KJ-method card."""
    model_config = ConfigDict(extra="forbid")

    cardText: str = Field(min_length=1, max_length=2000)
    context: str | None = Field(default=None, max_length=2000)


class RefineCardTextResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    refinedText: str
    reasoning: str | None = None


class SuggestCardGroupsRequest(BaseModel):
    """Request to suggest groupings/islands for a set of KJ-method cards."""
    model_config = ConfigDict(extra="forbid")

    cards: list[_CardRef] = Field(min_length=2, max_length=100)


class _CardRef(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(min_length=1, max_length=256)
    text: str = Field(min_length=1, max_length=2000)


class SuggestCardGroupsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    groups: list[_SuggestedGroup]


class _SuggestedGroup(BaseModel):
    model_config = ConfigDict(extra="forbid")
    label: str
    cardIds: list[str]
    rationale: str | None = None


class DetectContradictionRequest(BaseModel):
    """Request to detect contradiction between two KJ-method cards."""
    model_config = ConfigDict(extra="forbid")

    cardA: _CardRef
    cardB: _CardRef


class DetectContradictionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    hasContradiction: bool
    explanation: str | None = None


class AssessCardImportanceRequest(BaseModel):
    """Request to assess the importance/centrality of KJ-method cards."""
    model_config = ConfigDict(extra="forbid")

    cards: list[_CardRef] = Field(min_length=1, max_length=100)


class AssessCardImportanceResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    assessments: list[_CardAssessment]


class _CardAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cardId: str
    importance: str  # "high" | "medium" | "low"
    rationale: str | None = None

    proposalId: str = Field(min_length=1)


class SuggestDocumentTitleRequest(BaseModel):
    """Request to suggest document titles based on content overview."""
    model_config = ConfigDict(extra="forbid")

    # Island titles and a sample of reviewed card texts to base suggestions on.
    islandTitles: list[str] = Field(min_length=0, max_length=50)
    cardTexts: list[str] = Field(min_length=0, max_length=50)
    currentTitle: str | None = Field(default=None, max_length=500)


class _DocumentTitleCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=1, max_length=500)


class SuggestDocumentTitleResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidates: list[_DocumentTitleCandidate] = Field(min_length=1, max_length=3)
    status: Literal["accepted", "rejected", "held"]
    reviewState: Literal["unreviewed"]
    recordedAt: str = Field(min_length=1)
