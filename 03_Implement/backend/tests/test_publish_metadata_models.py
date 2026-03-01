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


def test_public_pack_manifest_visibility_fallback_and_filtering() -> None:
    manifest = PublicPackManifest.model_validate(
        {
            "defaultPackId": "main",
            "packs": [
                {"id": "main", "documentPath": "main.document.json", "viewPath": "main.view.json"},
                {"id": "", "documentPath": "skip.document.json"},
                {"id": "broken", "documentPath": 123},
            ],
        }
    )

    assert manifest.defaultPackId == "main"
    assert len(manifest.packs) == 1
    assert manifest.packs[0].id == "main"
    assert manifest.packs[0].visibility == "Public"
