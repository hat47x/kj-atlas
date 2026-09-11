from __future__ import annotations

import pytest

from sui_sensemaking_api import main as main_module
from sui_sensemaking_api.settings import Settings


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
    monkeypatch.setenv("SUI_RUNTIME_PROFILE", "local-dev")
    monkeypatch.setenv("SUI_DATABASE_URL", "sqlite:///./sui_sensemaking.db")
    monkeypatch.setenv("SUI_LLM_PROVIDER", "none")
    monkeypatch.setenv("SUI_APP_REVISION", raw_revision)

    built = Settings()
    assert built.app_revision == expected_revision

    monkeypatch.setattr(main_module.settings, "app_revision", built.app_revision)
    assert main_module.version()["revision"] == expected_revision
