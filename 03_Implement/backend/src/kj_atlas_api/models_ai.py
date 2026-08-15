from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from kj_atlas_api.models import DocumentV1, NarrativeCheckCounts


# DATA-CONTRACT-02 (案b): align the API contract with the persistence bound.
# The ai_proposals / decision tables enforce `length(source_bundle_hash) = 64`,
# so a `mock:`-prefixed (69-char) hash passed the request pattern but failed at
# DB flush with a misleading 409. The docs CE4 path keeps its OWN mock: gate
# (runtime policy `ce4_source_bundle_hash_allow_mock`); the proposal path now
# accepts only the 64-char SHA-256 form, matching what can be persisted.
SOURCE_BUNDLE_HASH_PATTERN = r"^[0-9a-f]{64}$"


class ProviderStatusResponse(BaseModel):
    """PROV-VIS-01 (ADR-0050 D1): read-only echo of the configured LLM
    provider kind. This is NOT a live connectivity check — it reports the
    resolved provider_kind only. "fixture" is a test-only provider selected
    directly in Python tests, never via KJ_ATLAS_LLM_PROVIDER, so it is not a
    reachable runtime value here."""

    model_config = ConfigDict(extra="forbid")

    providerKind: Literal["none", "local", "large-scale"]
    # OPS-LLM-COST-01 (段階2): in-process LLM call counts per provider kind
    # (plus "total"). Referenceable so an operator can see external
    # (large-scale) call volume. Empty until the first LLM call.
    callCounts: dict[str, int] = Field(default_factory=dict)


class NarrativeIssueReference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    kind: Literal["card", "island"]


class NarrativeIssue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    severity: Literal["info", "warn", "error"]
    message: str = Field(min_length=1)
    references: list[NarrativeIssueReference] | None = None
    # A/B cross-check direction when this issue is an A/B mismatch
    # (kj_technique.md §5). Optional for backward compatibility with older
    # model responses.
    direction: Literal["b_missing_in_a", "a_missing_in_b"] | None = None


class CheckNarrativeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    doc: DocumentV1
    narrativeText: str = Field(min_length=1)
    basedOnReadingOrder: list[str] | None = None
    # SEC-AI-SAFEMODE-01 (ADR-0068 D1=C/D3=A): optional, fail-closed relaxation.
    allowUnreviewedText: bool | None = None


class CheckNarrativeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    issues: list[NarrativeIssue]
    # A/B cross-check totals per direction (kj_technique.md §5: 報告は件数で).
    counts: NarrativeCheckCounts | None = None


class GenerateNarrativeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    doc: DocumentV1
    narrativeTitle: str | None = None
    # SEC-AI-SAFEMODE-01 (ADR-0068 D1=C/D3=A): optional, fail-closed relaxation.
    allowUnreviewedText: bool | None = None
    # AI-MODEL-GOVERNANCE-01 (R2): per-operation model override (allowlist-checked).
    model: str | None = Field(default=None, max_length=256)


class GenerateNarrativeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str
    basedOnReadingOrder: list[str]
    warnings: list[str] | None = None


class SuggestIslandSummaryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    doc: DocumentV1
    islandId: str = Field(min_length=1)
    # SEC-AI-SAFEMODE-01 (ADR-0068 D1=C/D3=A): optional, fail-closed relaxation.
    allowUnreviewedText: bool | None = None
    # AI-MODEL-GOVERNANCE-01 (R2): per-operation model override (allowlist-checked).
    model: str | None = Field(default=None, max_length=256)


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
    # SEC-AI-SAFEMODE-01 (ADR-0068 D1=C/D3=A): optional, fail-closed relaxation.
    allowUnreviewedText: bool | None = None


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
    # SEC-AI-SAFEMODE-01 (ADR-0068 D1=C/D3=A): optional, fail-closed relaxation.
    allowUnreviewedText: bool | None = None
    # AI-MODEL-GOVERNANCE-01 (R2): per-operation model override (allowlist-checked).
    model: str | None = Field(default=None, max_length=256)


class ProposalDecisionAuditRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    docId: str = Field(min_length=1, max_length=128)
    proposalId: str = Field(min_length=1, max_length=128)
    sourceBundleHash: str = Field(pattern=SOURCE_BUNDLE_HASH_PATTERN)
    idempotencyKey: str = Field(min_length=1, max_length=256)
    decision: Literal["adopt", "reject", "hold"]
    reason: str | None = Field(default=None, max_length=1000)


class ProposalDecisionAuditResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    recorded: Literal[True] = True
    eventId: str = Field(min_length=1)
    proposalId: str = Field(min_length=1)
    status: Literal["accepted", "rejected", "held"]
    reviewState: Literal["unreviewed"] = "unreviewed"
    recordedAt: str = Field(min_length=1)


class ExternalAgentProposalRegistrationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    docId: str = Field(min_length=1, max_length=128)
    taskId: str = Field(min_length=1, max_length=128)
    baseDocSignature: str = Field(min_length=1, max_length=512)
    sourceBundleHash: str = Field(pattern=SOURCE_BUNDLE_HASH_PATTERN)
    queryCanonicalHash: str = Field(pattern=SOURCE_BUNDLE_HASH_PATTERN)
    proposalId: str = Field(min_length=1, max_length=128)
    proposalKind: Literal[
        "island_title",
        "merge_candidate",
        "narrative_draft",
        "opposing_viewpoint",
        "critique",
        "patch",
    ]
    proposalFingerprint: str = Field(pattern=SOURCE_BUNDLE_HASH_PATTERN)
    provenanceLevel: Literal["user_presented_unsigned"]


class ExternalAgentTaskRegistrationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    docId: str = Field(min_length=1, max_length=128)
    taskId: str = Field(min_length=1, max_length=128)
    baseDocSignature: str = Field(min_length=1, max_length=512)
    sourceBundleHash: str = Field(pattern=SOURCE_BUNDLE_HASH_PATTERN)
    queryCanonicalHash: str = Field(pattern=SOURCE_BUNDLE_HASH_PATTERN)
    taskKind: Literal[
        "island_titles",
        "merge_candidates",
        "narrative_draft",
        "opposing_viewpoints",
        "critique_suggestions",
        "free_analysis",
    ]
    provenanceLevel: Literal["user_presented_unsigned"]


class ExternalAgentTaskRegistrationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    registered: Literal[True] = True
    taskId: str
    provenanceLevel: Literal["user_presented_unsigned"]


class ExternalAgentProposalRegistrationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    registered: Literal[True] = True
    proposalId: str
    provenanceLevel: Literal["user_presented_unsigned"]


class ExternalAgentProposalDecisionRequest(ProposalDecisionAuditRequest):
    provenanceLevel: Literal["user_presented_unsigned"]


# ---------------------------------------------------------------------------
# ADR-0064: KJ-method card-level AI operations
# ---------------------------------------------------------------------------


class RefineCardTextRequest(BaseModel):
    """Request to refine/improve the wording of a single KJ-method card."""

    model_config = ConfigDict(extra="forbid")

    cardText: str = Field(min_length=1, max_length=2000)
    context: str | None = Field(default=None, max_length=2000)
    # SEC-AI-SAFEMODE-02: this route has no document context, so the review
    # state travels with the request. textReviewed certifies the caller has
    # human-reviewed the input text; it defaults False (fail-closed) per
    # ADR-0068 D3=A (unspecified = SafeMode ON).
    textReviewed: bool = False
    # SEC-AI-SAFEMODE-01 (ADR-0068 D1=C/D3=A): optional, fail-closed relaxation.
    allowUnreviewedText: bool | None = None
    # AI-MODEL-GOVERNANCE-01 (R2): per-operation model override (allowlist-checked).
    model: str | None = Field(default=None, max_length=256)


class RefineCardTextResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    refinedText: str
    reasoning: str | None = None


class SuggestCardGroupsRequest(BaseModel):
    """Request to suggest groupings/islands for a set of KJ-method cards."""

    model_config = ConfigDict(extra="forbid")

    cards: list[_CardRef] = Field(min_length=2, max_length=100)
    # SEC-AI-SAFEMODE-01 (ADR-0068 D1=C/D3=A): optional, fail-closed relaxation.
    allowUnreviewedText: bool | None = None
    # AI-MODEL-GOVERNANCE-01 (R2): per-operation model override (allowlist-checked).
    model: str | None = Field(default=None, max_length=256)


class _CardRef(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(min_length=1, max_length=256)
    text: str = Field(min_length=1, max_length=2000)
    # SEC-AI-SAFEMODE-02: no-doc routes take card text directly, so the review
    # state travels with each card. Defaults False (unreviewed, fail-closed) per
    # ADR-0068 D3=A.
    textReviewed: bool = False


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
    # SEC-AI-SAFEMODE-01 (ADR-0068 D1=C/D3=A): optional, fail-closed relaxation.
    allowUnreviewedText: bool | None = None


class DetectContradictionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    hasContradiction: bool
    explanation: str | None = None


class SuggestDocumentTitleRequest(BaseModel):
    """Request to suggest document titles based on content overview."""

    model_config = ConfigDict(extra="forbid")

    # Island titles and a sample of reviewed card texts to base suggestions on.
    islandTitles: list[str] = Field(min_length=0, max_length=50)
    cardTexts: list[str] = Field(min_length=0, max_length=50)
    currentTitle: str | None = Field(default=None, max_length=500)
    # SEC-AI-SAFEMODE-02: this no-doc route forwards cardTexts to the LLM, so
    # the review state travels with the request. textReviewed certifies the
    # input texts are human-reviewed; defaults False (fail-closed, ADR-0068
    # D3=A).
    textReviewed: bool = False
    # SEC-AI-SAFEMODE-01 (ADR-0068 D1=C/D3=A): optional, fail-closed relaxation.
    allowUnreviewedText: bool | None = None
    # AI-MODEL-GOVERNANCE-01 (R2): per-operation model override (allowlist-checked).
    model: str | None = Field(default=None, max_length=256)


class _DocumentTitleCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=1, max_length=500)


class SuggestDocumentTitleResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidates: list[_DocumentTitleCandidate] = Field(min_length=1, max_length=3)
