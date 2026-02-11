from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field
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
    title: str | None = None


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
    cards: list[Card]
    edges: list[EdgeV2]
    islands: list[Island]


DocumentPayload = Annotated[DocumentV1 | DocumentV2, Field(discriminator="version")]


class SuggestLayoutRequest(BaseModel):
    doc: DocumentV2
    instruction: str | None = None


class SuggestLayoutResponse(BaseModel):
    suggestionId: str
    suggestedDoc: DocumentV2
    notes: str | None = None
