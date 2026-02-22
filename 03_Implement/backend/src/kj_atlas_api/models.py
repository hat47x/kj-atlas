from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field, model_validator
from sqlalchemy import Integer, Text
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
    parentIslandId: str | None = None
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
