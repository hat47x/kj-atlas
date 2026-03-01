import pytest

from kj_atlas_api.models_publish import PublicPackManifest, ViewMetadata


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
    with pytest.raises(Exception) as excinfo:
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
    with pytest.raises(Exception) as excinfo:
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
