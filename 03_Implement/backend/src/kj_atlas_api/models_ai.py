from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from kj_atlas_api.models import DocumentV2


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

    doc: DocumentV2
    narrativeText: str = Field(min_length=1)
    basedOnReadingOrder: list[str] | None = None


class CheckNarrativeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    issues: list[NarrativeIssue]


class GenerateNarrativeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    doc: DocumentV2
    narrativeTitle: str | None = None


class GenerateNarrativeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str
    basedOnReadingOrder: list[str]
    warnings: list[str] | None = None


class SuggestIslandSummaryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    doc: DocumentV2
    islandId: str = Field(min_length=1)


class SuggestIslandSummaryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summaryText: str = Field(min_length=1)
    groundingIds: list[str] = Field(min_length=1)
    warnings: list[str] | None = None
