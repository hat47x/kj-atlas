from __future__ import annotations

import pytest

from kj_atlas_api import main as main_module
from kj_atlas_api.settings import Settings


@pytest.mark.parametrize(
    ("raw_revision", "expected_revision"),
    [
        ("rev-2026.09.06_1", "rev-2026.09.06_1"),
        ("a" * 64, "a" * 64),
        ("", "unknown"),
        (" release-1 ", "unknown"),
        ("release+1", "unknown"),
        ("feature/revision", "unknown"),
        ("line\nbreak", "unknown"),
        ("a" * 65, "unknown"),
    ],
)
def test_app_revision_is_canonicalized_before_observability_surfaces(
    monkeypatch: pytest.MonkeyPatch,
    raw_revision: str,
    expected_revision: str,
) -> None:
    monkeypatch.setenv("KJ_ATLAS_RUNTIME_PROFILE", "local-dev")
    monkeypatch.setenv("KJ_ATLAS_DATABASE_URL", "sqlite:///./kj_atlas.db")
    monkeypatch.setenv("KJ_ATLAS_LLM_PROVIDER", "none")
    monkeypatch.setenv("KJ_ATLAS_APP_REVISION", raw_revision)

    built = Settings()
    assert built.app_revision == expected_revision

    monkeypatch.setattr(main_module.settings, "app_revision", built.app_revision)
    assert main_module.version()["revision"] == expected_revision
