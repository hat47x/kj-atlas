import pytest
from pydantic import ValidationError

from kj_atlas_api.models_publish import (
    PublicPackManifest,
    ViewMetadata,
    validate_public_pack_manifest,
    validate_view_metadata,
)


def test_view_metadata_visibility_fallback_for_legacy_payload() -> None:
    metadata = ViewMetadata.model_validate(
        {
            "version": "1",
            "generatedAt": "2026-03-01T00:00:00.000Z",
            "docSignature": "doc-legacy",
        }
    )

    assert metadata.visibility == "Restricted"


def test_public_pack_manifest_visibility_fallback_for_legacy_payload() -> None:
    manifest = PublicPackManifest.model_validate(
        {
            "defaultPackId": "main",
            "packs": [
                {"id": "main", "documentPath": "main.document.json", "viewPath": "main.view.json"},
            ],
        }
    )

    assert manifest.defaultPackId == "main"
    assert len(manifest.packs) == 1
    assert manifest.packs[0].id == "main"
    assert manifest.packs[0].visibility == "Public"


def test_view_metadata_rejects_invalid_visibility() -> None:
    with pytest.raises(ValidationError) as excinfo:
        ViewMetadata.model_validate(
            {
                "version": "1",
                "generatedAt": "2026-03-01T00:00:00.000Z",
                "docSignature": "doc-invalid",
                "visibility": "FriendsOnly",
            }
        )

    assert "visibility" in str(excinfo.value)


def test_public_pack_manifest_rejects_invalid_entry_instead_of_filtering() -> None:
    with pytest.raises(ValidationError) as excinfo:
        PublicPackManifest.model_validate(
            {
                "packs": [
                    {"id": "ok", "documentPath": "ok.document.json"},
                    {"id": "broken", "documentPath": 123},
                ]
            }
        )

    assert "documentPath" in str(excinfo.value)


def test_public_pack_manifest_accepts_all_visibility_enum_values() -> None:
    manifest = PublicPackManifest.model_validate(
        {
            "packs": [
                {"id": "public", "documentPath": "public.document.json", "visibility": "Public"},
                {"id": "unlisted", "documentPath": "unlisted.document.json", "visibility": "Unlisted"},
                {"id": "org", "documentPath": "org.document.json", "visibility": "Org"},
                {"id": "restricted", "documentPath": "restricted.document.json", "visibility": "Restricted"},
            ]
        }
    )

    assert [entry.visibility for entry in manifest.packs] == ["Public", "Unlisted", "Org", "Restricted"]


def test_view_metadata_accepts_all_visibility_enum_values() -> None:
    visibilities = ["Public", "Unlisted", "Org", "Restricted"]

    loaded = [
        ViewMetadata.model_validate(
            {
                "version": "1",
                "generatedAt": "2026-03-01T00:00:00.000Z",
                "docSignature": f"doc-{visibility.lower()}",
                "visibility": visibility,
            }
        )
        for visibility in visibilities
    ]

    assert [metadata.visibility for metadata in loaded] == visibilities


@pytest.mark.parametrize("invalid_visibility", ["public", "", None, 1, {"value": "Org"}])
def test_view_metadata_rejects_non_enum_visibility_types(invalid_visibility: object) -> None:
    with pytest.raises(ValidationError) as excinfo:
        ViewMetadata.model_validate(
            {
                "version": "1",
                "generatedAt": "2026-03-01T00:00:00.000Z",
                "docSignature": "doc-invalid-typed",
                "visibility": invalid_visibility,
            }
        )

    assert "visibility" in str(excinfo.value)


@pytest.mark.parametrize("invalid_visibility", ["private", "", None, 1, {"value": "Org"}])
def test_public_pack_manifest_rejects_non_enum_visibility_types(invalid_visibility: object) -> None:
    with pytest.raises(ValidationError) as excinfo:
        PublicPackManifest.model_validate(
            {
                "packs": [
                    {
                        "id": "main",
                        "documentPath": "main.document.json",
                        "viewPath": "main.view.json",
                        "visibility": invalid_visibility,
                    }
                ]
            }
        )

    assert "visibility" in str(excinfo.value)


def test_view_metadata_roundtrip_keeps_visibility_after_put_get_cycle() -> None:
    put_payload = {
        "version": "1",
        "generatedAt": "2026-03-01T00:00:00.000Z",
        "docSignature": "doc-roundtrip",
        "visibility": "Org",
    }

    stored = ViewMetadata.model_validate(put_payload)
    get_payload = stored.model_dump(mode="json")
    loaded = ViewMetadata.model_validate(get_payload)

    assert loaded.visibility == "Org"
    assert get_payload["visibility"] == "Org"


def test_view_metadata_roundtrip_fills_missing_visibility_and_emits_it() -> None:
    legacy_put_payload = {
        "version": "1",
        "generatedAt": "2026-03-01T00:00:00.000Z",
        "docSignature": "doc-legacy-roundtrip",
    }

    stored = ViewMetadata.model_validate(legacy_put_payload)
    get_payload = stored.model_dump(mode="json")

    assert stored.visibility == "Restricted"
    assert get_payload["visibility"] == "Restricted"


def test_view_metadata_strict_validation_rejects_missing_visibility() -> None:
    with pytest.raises(ValidationError) as excinfo:
        validate_view_metadata(
            {
                "version": "1",
                "generatedAt": "2026-03-01T00:00:00.000Z",
                "docSignature": "doc-strict",
            },
            strict=True,
        )

    assert "visibility" in str(excinfo.value)


def test_view_metadata_compat_validation_accepts_missing_visibility() -> None:
    metadata = validate_view_metadata(
        {
            "version": "1",
            "generatedAt": "2026-03-01T00:00:00.000Z",
            "docSignature": "doc-compat",
        },
        strict=False,
    )

    assert metadata.visibility == "Restricted"


def test_public_pack_manifest_roundtrip_fills_missing_visibility_and_emits_it() -> None:
    legacy_manifest = {
        "defaultPackId": "main",
        "packs": [
            {"id": "main", "documentPath": "main.document.json", "viewPath": "main.view.json"},
        ],
    }

    stored = PublicPackManifest.model_validate(legacy_manifest)
    get_payload = stored.model_dump(mode="json")
    loaded = PublicPackManifest.model_validate(get_payload)

    assert stored.packs[0].visibility == "Public"
    assert get_payload["packs"][0]["visibility"] == "Public"
    assert loaded.packs[0].visibility == "Public"


def test_public_pack_manifest_strict_validation_rejects_missing_visibility() -> None:
    with pytest.raises(ValidationError) as excinfo:
        validate_public_pack_manifest(
            {
                "defaultPackId": "main",
                "packs": [
                    {
                        "id": "main",
                        "documentPath": "main.document.json",
                    }
                ],
            },
            strict=True,
        )

    assert "visibility" in str(excinfo.value)


def test_public_pack_manifest_compat_validation_accepts_missing_visibility() -> None:
    manifest = validate_public_pack_manifest(
        {
            "defaultPackId": "main",
            "packs": [
                {
                    "id": "main",
                    "documentPath": "main.document.json",
                }
            ],
        },
        strict=False,
    )

    assert manifest.packs[0].visibility == "Public"
