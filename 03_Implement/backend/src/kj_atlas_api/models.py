from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from sqlalchemy import Index, Integer, Text
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


RELATION_SUMMARY_TEXT_MAX_LENGTH = 4000


class Base(DeclarativeBase):
    pass


class DocumentRow(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    updated_at: Mapped[str] = mapped_column(Text, nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)


class UserRow(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    display_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    email: Mapped[str | None] = mapped_column(Text, nullable=True)
    lifecycle_state: Mapped[str] = mapped_column(Text, nullable=False, default="active")
    created_at: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[str] = mapped_column(Text, nullable=False)


class UserIdentityRow(Base):
    __tablename__ = "user_identities"
    __table_args__ = (UniqueConstraint("provider", "external_uid", name="uq_user_identities_provider_external_uid"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(Text, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider: Mapped[str] = mapped_column(Text, nullable=False)
    external_uid: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(Text, nullable=False)


class MergeDecisionLogRow(Base):
    __tablename__ = "merge_decision_logs"
    __table_args__ = (
        UniqueConstraint("doc_id", "decision_id", name="uq_merge_decision_logs_doc_decision"),
        Index("ix_merge_decision_logs_doc_group_id", "doc_id", "group_id", "id"),
        Index("ix_merge_decision_logs_doc_snapshot_id", "doc_id", "snapshot_version", "id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    doc_id: Mapped[str] = mapped_column(Text, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    decision_id: Mapped[str] = mapped_column(Text, nullable=False)
    group_id: Mapped[str] = mapped_column(Text, nullable=False)
    snapshot_version: Mapped[str] = mapped_column(Text, nullable=False)
    decided_at: Mapped[str] = mapped_column(Text, nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)


class Transform(BaseModel):
    panX: float
    panY: float
    zoom: float


class Card(BaseModel):
    id: str
    text: str
    x: float
    y: float
    mergedIntoCardId: str | None = Field(default=None, exclude_if=lambda value: value is None)
    repOf: list[str] | None = Field(default=None, exclude_if=lambda value: value is None)
    canonicalId: str | None = Field(default=None, exclude_if=lambda value: value is None)
    sources: list[str] | None = Field(default=None, exclude_if=lambda value: value is None)
    critique: str | None = None
    critiqueTags: list[str] | None = Field(default=None, exclude_if=lambda value: value is None)
    textReviewed: bool | None = Field(default=None, exclude_if=lambda value: value is None)


class CardV2(Card):
    textReviewed: bool | None = None


class EdgeV1(BaseModel):
    id: str
    fromId: str
    toId: str
    type: Literal["related"]


class EdgeV2(BaseModel):
    id: str
    fromId: str
    toId: str
    type: Literal["related", "negate"]


class Point(BaseModel):
    x: float
    y: float


class ShapeGeneratedFrom(BaseModel):
    cardIds: list[str]
    versionToken: str


class IslandShape(BaseModel):
    kind: Literal["rect", "polygon"]
    points: list[Point] | None = Field(default=None, exclude_if=lambda value: value is None)
    generatedFrom: ShapeGeneratedFrom | None = Field(default=None, exclude_if=lambda value: value is None)

    @model_validator(mode="after")
    def ensure_shape_points(self) -> "IslandShape":
        if self.kind == "polygon":
            if self.points is None or len(self.points) < 3:
                raise ValueError("polygon shape requires at least 3 points")
        elif self.points is not None:
            raise ValueError("rect shape must not include points")
        return self


class IslandGeometry(BaseModel):
    type: Literal["rect", "polygon"]
    x: float | None = Field(default=None, exclude_if=lambda value: value is None)
    y: float | None = Field(default=None, exclude_if=lambda value: value is None)
    w: float | None = Field(default=None, exclude_if=lambda value: value is None)
    h: float | None = Field(default=None, exclude_if=lambda value: value is None)
    points: list[Point] | None = Field(default=None, exclude_if=lambda value: value is None)
    polygon: dict[str, list[Point]] | None = Field(default=None, exclude_if=lambda value: value is None)

    @model_validator(mode="after")
    def ensure_geometry_polygon(self) -> "IslandGeometry":
        if self.type == "polygon":
            legacy_points = self.polygon.get("points") if self.polygon else None
            resolved_points = self.points if self.points is not None else legacy_points
            if resolved_points is None or len(resolved_points) < 3:
                raise ValueError("polygon geometry requires at least 3 points")
            self.points = resolved_points
            self.polygon = None
        else:
            if self.points is not None or self.polygon is not None:
                raise ValueError("rect geometry must not include polygon points")
        return self


class SummaryHistoryEntry(BaseModel):
    id: str
    createdAt: datetime
    fromText: str | None = Field(default=None, exclude_if=lambda value: value is None)
    toText: str | None = Field(default=None, exclude_if=lambda value: value is None)
    fromReviewed: bool | None = Field(default=None, exclude_if=lambda value: value is None)
    toReviewed: bool | None = Field(default=None, exclude_if=lambda value: value is None)
    changeKind: Literal["manual", "ai", "import", "unknown"]
    note: str | None = Field(default=None, exclude_if=lambda value: value is None)
    groundingIds: list[str] | None = Field(default=None, exclude_if=lambda value: value is None)


class Island(BaseModel):
    id: str
    cardIds: list[str]
    parentIslandId: str | None = Field(default=None, exclude_if=lambda value: value is None)
    placardCardId: str | None = Field(default=None, exclude_if=lambda value: value is None)
    collapsed: bool = False
    title: str | None = None
    titleReviewed: bool | None = Field(default=None, exclude_if=lambda value: value is None)
    summaryText: str | None = None
    summaryReviewed: bool | None = Field(default=None, exclude_if=lambda value: value is None)
    summaryGrounding: list[str] | None = Field(default=None, exclude_if=lambda value: value is None)
    summaryHistory: list[SummaryHistoryEntry] | None = Field(default=None, exclude_if=lambda value: value is None)
    imageUrl: str | None = None
    imageReviewed: bool | None = Field(default=None, exclude_if=lambda value: value is None)
    critique: str | None = None
    critiqueTags: list[str] | None = Field(default=None, exclude_if=lambda value: value is None)
    geometry: IslandGeometry | None = Field(default=None, exclude_if=lambda value: value is None)
    shape: IslandShape | None = Field(default=None, exclude_if=lambda value: value is None)
    shapeStale: bool | None = Field(default=None, exclude_if=lambda value: value is None)

    @model_validator(mode="after")
    def normalize_geometry_shape(self) -> "Island":
        if self.geometry is None and self.shape is not None:
            if self.shape.kind == "polygon" and self.shape.points is not None:
                self.geometry = IslandGeometry(type="polygon", points=self.shape.points)
            elif self.shape.kind == "rect":
                self.geometry = IslandGeometry(type="rect")
        elif self.shape is None and self.geometry is not None:
            if self.geometry.type == "polygon":
                points = self.geometry.points
                if points is not None:
                    self.shape = IslandShape(kind="polygon", points=points)
            else:
                self.shape = IslandShape(kind="rect")
        return self

    @model_validator(mode="after")
    def ensure_summary_review_default(self) -> "Island":
        if self.summaryText is not None and self.summaryReviewed is None:
            self.summaryReviewed = False
        return self


class NarrativeCheckReference(BaseModel):
    id: str
    kind: Literal["card", "island"]


class NarrativeCheckIssue(BaseModel):
    severity: Literal["info", "warn", "error"]
    message: str
    references: list[NarrativeCheckReference] | None = Field(default=None, exclude_if=lambda value: value is None)


class NarrativeCheck(BaseModel):
    id: str
    createdAt: datetime
    kind: Literal["consistency"]
    issues: list[NarrativeCheckIssue]


class Narrative(BaseModel):
    id: str
    title: str
    text: str
    createdAt: datetime | None = Field(default=None, exclude_if=lambda value: value is None)
    basedOnReadingOrder: list[str] | None = Field(default=None, exclude_if=lambda value: value is None)
    reviewed: bool
    checks: list[NarrativeCheck] | None = Field(default=None, exclude_if=lambda value: value is None)




class RelationSummaryHistoryEntry(BaseModel):
    id: str
    createdAt: datetime
    changeKind: Literal["ai", "manual", "rollback", "import", "unknown"]
    fromText: str | None = Field(default=None, exclude_if=lambda value: value is None)
    toText: str | None = Field(default=None, exclude_if=lambda value: value is None)
    fromReviewed: bool | None = Field(default=None, exclude_if=lambda value: value is None)
    toReviewed: bool | None = Field(default=None, exclude_if=lambda value: value is None)
    warningsSnapshot: list[str] | None = Field(default=None, exclude_if=lambda value: value is None)
    groundingCardIdsSnapshot: list[str] | None = Field(default=None, exclude_if=lambda value: value is None)
    groundingEdgeIdsSnapshot: list[str] | None = Field(default=None, exclude_if=lambda value: value is None)
    note: str | None = Field(default=None, exclude_if=lambda value: value is None)

class RelationSummary(BaseModel):
    id: str
    createdAt: datetime
    islandAId: str
    islandBId: str
    relationType: Literal["related", "negate", "unknown"]
    derived: bool
    text: str = Field(max_length=RELATION_SUMMARY_TEXT_MAX_LENGTH)
    reviewed: bool = False
    groundingCardIds: list[str]
    groundingEdgeIds: list[str]
    warnings: list[str] | None = Field(default=None, exclude_if=lambda value: value is None)
    sourceSignature: str
    history: list[RelationSummaryHistoryEntry] | None = Field(default=None, exclude_if=lambda value: value is None)




class PatchApplyStats(BaseModel):
    upsertCards: int
    deleteCards: int
    upsertIslands: int
    deleteIslands: int
    upsertEdges: int
    deleteEdges: int
    upsertRelationSummaries: int
    deleteRelationSummaries: int


class PatchApplyConflictMeta(BaseModel):
    totalConflicts: int
    chosenYours: int
    chosenTheirs: int
    chosenSkip: int


class PatchApplyLogEntry(BaseModel):
    id: str
    createdAt: datetime
    patchVersion: Literal["1"]
    patchTitle: str | None = Field(default=None, exclude_if=lambda value: value is None)
    baseDocSignature: str | None = Field(default=None, exclude_if=lambda value: value is None)
    patchSourceSignature: str | None = Field(default=None, exclude_if=lambda value: value is None)
    appliedOpIds: list[str]
    stats: PatchApplyStats
    conflictMeta: PatchApplyConflictMeta | None = Field(default=None, exclude_if=lambda value: value is None)
    note: str | None = Field(default=None, exclude_if=lambda value: value is None)


class DocumentV1(BaseModel):
    version: Literal[1]
    id: str
    title: str | None = None
    createdAt: datetime
    updatedAt: datetime
    transform: Transform
    cards: list[Card]
    edges: list[EdgeV1]




class MergeSuggestionDecision(BaseModel):
    id: str
    groupId: str
    decision: Literal["accept", "partial", "reject", "defer"]
    decidedAt: datetime
    cardIds: list[str]
    mergedTextDraft: str
    editedText: str
    rationale: str | None = Field(default=None, exclude_if=lambda value: value is None)


class MergeDecisionRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decisionId: str
    groupId: str
    action: Literal["accept", "partial", "reject", "defer"]
    selectedCardIds: list[str]
    note: str
    decidedBy: str
    decidedAt: datetime
    snapshotVersion: str


class SimilarCandidateScoreSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    min: float
    max: float
    avg: float


class SimilarCandidateGroup(BaseModel):
    model_config = ConfigDict(extra="forbid")

    groupId: str
    targetCardId: str
    candidateCardIds: list[str]
    scoreSummary: SimilarCandidateScoreSummary
    reasonCodes: list[str]
    snapshotVersion: str


class CandidateListViewModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generatedAt: datetime
    groups: list[SimilarCandidateGroup]
    totalGroupCount: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_total_group_count(self) -> "CandidateListViewModel":
        if self.totalGroupCount != len(self.groups):
            raise ValueError("totalGroupCount must equal len(groups)")
        return self


class CritiqueInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schemaVersion: Literal["1.0.0"]
    critiqueId: str
    targetRef: str
    critiqueType: Literal["too_close", "too_far", "not_the_same", "feels_off", "no_articulable_reason"]
    createdAt: datetime
    iteration: int = Field(ge=1)
    comment: str | None = Field(default=None, exclude_if=lambda value: value is None)
    constraintHints: list[str] | None = Field(default=None, exclude_if=lambda value: value is None)

    @field_validator("targetRef")
    @classmethod
    def validate_target_ref_kind(cls, value: str) -> str:
        allowed_prefixes = ("card:", "cluster:", "edge:", "proposal:")
        if not value.startswith(allowed_prefixes):
            raise ValueError("targetRef must start with card:, cluster:, edge:, or proposal:")
        return value


class ReproposalDiffOp(BaseModel):
    model_config = ConfigDict(extra="forbid")

    opId: str
    opType: Literal["add", "remove", "move", "regroup", "relabel"]
    targetRef: str
    before: dict[str, object] | None = None
    after: dict[str, object] | None = None

    @model_validator(mode="after")
    def validate_reversible_payload(self) -> "ReproposalDiffOp":
        if self.before is None and self.after is None:
            raise ValueError("before or after must be provided")
        return self


class ReproposalDiff(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schemaVersion: Literal["1.0.0"]
    proposalId: str
    basedOnIteration: int = Field(ge=1)
    diffOps: list[ReproposalDiffOp] = Field(min_length=1)
    traceKey: str
    rationale: str | None = Field(default=None, exclude_if=lambda value: value is None)

    @model_validator(mode="after")
    def validate_required_before_after(self) -> "ReproposalDiff":
        for op in self.diffOps:
            if op.before is None:
                raise ValueError("diffOps.before is required by A1-REDIFF-IF")
            if op.after is None:
                raise ValueError("diffOps.after is required by A1-REDIFF-IF")
        return self


class ReviewAttribution(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schemaVersion: Literal["1.0.0"]
    reviewState: Literal["unreviewed", "human_reviewed"]
    reviewedAt: datetime | None = None
    reviewerRef: str | None = Field(default=None, min_length=1)
    auditRecordedAt: datetime
    overridePolicy: Literal["human_dual_control_only"] = "human_dual_control_only"
    reviewContext: str | None = Field(default=None, exclude_if=lambda value: value is None)
    ownerRef: str | None = Field(default=None, exclude_if=lambda value: value is None)

    @field_validator("reviewerRef")
    @classmethod
    def validate_reviewer_ref_opaque(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if "@" in value:
            raise ValueError("reviewerRef must be opaque and must not contain email-like identifiers")
        return value

    @field_validator("ownerRef")
    @classmethod
    def validate_owner_ref_opaque(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if "@" in value:
            raise ValueError("ownerRef must be opaque and must not contain email-like identifiers")
        return value

    @model_validator(mode="after")
    def validate_human_review_transition(self) -> "ReviewAttribution":
        if self.reviewedAt is None:
            raise ValueError("reviewedAt is required by A1-ATTR-IF")
        if self.reviewerRef is None:
            raise ValueError("reviewerRef is required by A1-ATTR-IF")
        return self


class DeterministicTieBreak(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schemaVersion: Literal["1.0.0"]
    order: tuple[
        Literal["padding_compliance"],
        Literal["self_intersection_avoidance"],
        Literal["minimum_area_delta"],
        Literal["minimum_vertex_count"],
    ] = (
        "padding_compliance",
        "self_intersection_avoidance",
        "minimum_area_delta",
        "minimum_vertex_count",
    )

class DocumentV2(BaseModel):
    version: Literal[2]
    id: str
    title: str | None = None
    createdAt: datetime
    updatedAt: datetime
    transform: Transform
    cards: list[CardV2]
    edges: list[EdgeV2]
    islands: list[Island]
    readingOrder: list[str] | None = Field(default=None, exclude_if=lambda value: value is None)
    narratives: list[Narrative] | None = Field(default=None, exclude_if=lambda value: value is None)
    relationSummaries: list[RelationSummary] | None = Field(default=None, exclude_if=lambda value: value is None)
    patchApplyLog: list[PatchApplyLogEntry] | None = Field(default=None, exclude_if=lambda value: value is None)
    mergeSuggestionDecisions: list[MergeSuggestionDecision] | None = Field(default=None, exclude_if=lambda value: value is None)
    critiqueInputs: list[CritiqueInput] | None = Field(default=None, exclude_if=lambda value: value is None)
    reproposalDiffs: list[ReproposalDiff] | None = Field(default=None, exclude_if=lambda value: value is None)
    reviewAttribution: ReviewAttribution | None = Field(default=None, exclude_if=lambda value: value is None)
    deterministicTieBreak: DeterministicTieBreak | None = Field(default=None, exclude_if=lambda value: value is None)


DocumentPayload = Annotated[DocumentV1 | DocumentV2, Field(discriminator="version")]


class SuggestLayoutRequest(BaseModel):
    doc: DocumentV2
    instruction: str | None = None


class SuggestLayoutResponse(BaseModel):
    suggestionId: str
    suggestedDoc: DocumentV2
    notes: str | None = None


class MergeSuggestion(BaseModel):
    groupId: str
    cardIds: list[str]
    mergedTextDraft: str
    rationale: str | None = None


class SuggestMergesRequest(BaseModel):
    doc: DocumentV2
    instruction: str | None = None


class SuggestMergesResponse(BaseModel):
    suggestions: list[MergeSuggestion]
