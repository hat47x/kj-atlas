from __future__ import annotations

from datetime import date, timedelta

import pytest

from kj_atlas_api import settings as settings_module
from kj_atlas_api.settings import LEGACY_ENV_COMPAT_DEADLINE, Settings


@pytest.mark.parametrize(
    ("legacy_key", "canonical_key", "legacy_value", "canonical_value", "field_name"),
    [
        (
            "DATABASE_URL",
            "KJ_ATLAS_DATABASE_URL",
            "sqlite:///./legacy.db",
            "sqlite:///./canonical.db",
            "database_url",
        ),
        (
            "LLM_PROVIDER",
            "KJ_ATLAS_LLM_PROVIDER",
            "local",
            "none",
            "llm_provider",
        ),
        (
            "AUDIT_TRANSPORT",
            "KJ_ATLAS_AUDIT_TRANSPORT",
            "http",
            "noop",
            "audit_transport",
        ),
    ],
)
def test_canonical_env_key_wins_over_legacy_key(
    monkeypatch: pytest.MonkeyPatch,
    legacy_key: str,
    canonical_key: str,
    legacy_value: str,
    canonical_value: str,
    field_name: str,
) -> None:
    monkeypatch.setenv(legacy_key, legacy_value)
    monkeypatch.setenv(canonical_key, canonical_value)

    loaded = Settings()

    assert getattr(loaded, field_name) == canonical_value


def test_legacy_key_is_rejected_before_deadline(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./legacy-before-deadline.db")
    monkeypatch.delenv("KJ_ATLAS_DATABASE_URL", raising=False)
    monkeypatch.setattr(
        settings_module,
        "_current_utc_date",
        lambda: LEGACY_ENV_COMPAT_DEADLINE - timedelta(days=1),
    )

    with pytest.raises(ValueError, match="Legacy env keys are no longer supported"):
        Settings()


def test_legacy_key_fails_after_deadline_when_canonical_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./legacy-after-deadline.db")
    monkeypatch.delenv("KJ_ATLAS_DATABASE_URL", raising=False)
    monkeypatch.setattr(
        settings_module,
        "_current_utc_date",
        lambda: LEGACY_ENV_COMPAT_DEADLINE + timedelta(days=1),
    )

    with pytest.raises(ValueError, match="Legacy env keys are no longer supported"):
        Settings()


def test_deadline_constant_is_fixed() -> None:
    assert LEGACY_ENV_COMPAT_DEADLINE == date(2026, 12, 31)
