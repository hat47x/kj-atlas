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


class Island(BaseModel):
    id: str
    cardIds: list[str]
    parentIslandId: str | None = None
    collapsed: bool = False
    title: str | None = None
    titleReviewed: bool | None = Field(default=None, exclude_if=lambda value: value is None)
    summaryText: str | None = None
    summaryReviewed: bool | None = Field(default=None, exclude_if=lambda value: value is None)
    imageUrl: str | None = None
    imageReviewed: bool | None = Field(default=None, exclude_if=lambda value: value is None)
    critique: str | None = None
    critiqueTags: list[str] | None = Field(default=None, exclude_if=lambda value: value is None)

    @model_validator(mode="after")
    def ensure_summary_review_default(self) -> "Island":
        if self.summaryText is not None and self.summaryReviewed is None:
            self.summaryReviewed = False
        return self


class Narrative(BaseModel):
    id: str
    title: str | None = None
    createdAt: datetime
    basedOnReadingOrder: list[str]
    text: str
    reviewed: bool = False
    notes: str | None = None


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
