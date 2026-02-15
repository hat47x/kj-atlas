from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field, model_validator
from sqlalchemy import Integer, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


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
    shape: IslandShape | None = Field(default=None, exclude_if=lambda value: value is None)
    shapeStale: bool | None = Field(default=None, exclude_if=lambda value: value is None)

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
