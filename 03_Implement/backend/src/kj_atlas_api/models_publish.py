from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

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
