from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, ValidationError

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


def validate_view_metadata(payload: object, *, strict: bool = False) -> ViewMetadata:
    """Validate view metadata.

    strict=False keeps backward compatibility by filling missing visibility with
    the model default. strict=True requires the visibility field to be provided.
    """

    metadata = ViewMetadata.model_validate(payload)
    if strict and (not isinstance(payload, dict) or "visibility" not in payload):
        raise ValidationError.from_exception_data(
            title="ViewMetadata",
            line_errors=[
                {
                    "type": "missing",
                    "loc": ("visibility",),
                    "input": payload,
                }
            ],
        )
    return metadata


def validate_public_pack_manifest(payload: object, *, strict: bool = False) -> PublicPackManifest:
    """Validate public pack manifest.

    strict=False keeps backward compatibility by filling missing visibility with
    the model default. strict=True requires every pack entry to provide visibility.
    """

    manifest = PublicPackManifest.model_validate(payload)
    if strict and isinstance(payload, dict):
        packs = payload.get("packs")
        if isinstance(packs, list):
            for index, entry in enumerate(packs):
                if isinstance(entry, dict) and "visibility" not in entry:
                    raise ValidationError.from_exception_data(
                        title="PublicPackManifest",
                        line_errors=[
                            {
                                "type": "missing",
                                "loc": ("packs", index, "visibility"),
                                "input": entry,
                            }
                        ],
                    )
    return manifest
