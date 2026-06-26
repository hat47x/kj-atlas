from __future__ import annotations

from datetime import date, timedelta

import pytest

from kj_atlas_api import settings as settings_module
from kj_atlas_api.settings import LEGACY_ENV_COMPAT_DEADLINE, Settings


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
