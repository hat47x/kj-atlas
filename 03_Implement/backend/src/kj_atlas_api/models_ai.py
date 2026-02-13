from typing import Literal

from pydantic import BaseModel, ConfigDict

from kj_atlas_api.models import DocumentV2


class NarrativeIssueReference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    kind: Literal["card", "island"]


class NarrativeIssue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    severity: Literal["info", "warn", "error"]
    message: str
    references: list[NarrativeIssueReference] | None = None


class CheckNarrativeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    doc: DocumentV2
    narrativeText: str
    basedOnReadingOrder: list[str] | None = None


class CheckNarrativeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    issues: list[NarrativeIssue]
