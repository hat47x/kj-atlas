from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

PublishVisibility = Literal["Public", "Unlisted", "Org", "Restricted"]


class ViewMetadata(BaseModel):
    version: Literal["1"]
    generatedAt: str
    docSignature: str
    visibility: PublishVisibility = "Restricted"


class PublicPackManifestEntry(BaseModel):
    id: str
    documentPath: str
    viewPath: str | None = None
    title: str | None = None
    enforceSafeMode: bool | None = None
    readOnly: bool | None = None
    visibility: PublishVisibility = "Public"


class PublicPackManifest(BaseModel):
    defaultPackId: str | None = None
    packs: list[PublicPackManifestEntry] = Field(default_factory=list)

    @field_validator("packs", mode="before")
    @classmethod
    def _drop_invalid_entries(cls, value: object) -> list[dict[str, object]]:
        if not isinstance(value, list):
            return []

        validated: list[dict[str, object]] = []
        for item in value:
            if not isinstance(item, dict):
                continue
            if not isinstance(item.get("id"), str) or not item["id"].strip():
                continue
            if not isinstance(item.get("documentPath"), str) or not item["documentPath"].strip():
                continue
            validated.append(item)
        return validated
