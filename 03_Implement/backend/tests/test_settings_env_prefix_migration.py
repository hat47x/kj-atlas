from __future__ import annotations

import os

import pytest

from kj_atlas_api.settings import LEGACY_ENV_KEYS, Settings


def _unset_related_envs() -> None:
    for key in list(os.environ):
        if key.startswith("KJ_ATLAS_") or key in LEGACY_ENV_KEYS:
            os.environ.pop(key, None)


def test_settings_uses_prefixed_key(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    _unset_related_envs()
    monkeypatch.setenv("KJ_ATLAS_DATABASE_URL", "sqlite:///./canonical.db")

    loaded = Settings()

    assert loaded.database_url == "sqlite:///./canonical.db"


def test_settings_rejects_legacy_key(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    _unset_related_envs()
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./legacy.db")

    with pytest.raises(ValueError, match="Legacy environment keys are not supported"):
        Settings()


def test_settings_rejects_mixed_new_and_legacy_keys(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    _unset_related_envs()
    monkeypatch.setenv("KJ_ATLAS_DATABASE_URL", "sqlite:///./canonical.db")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./legacy.db")

    with pytest.raises(ValueError, match="DATABASE_URL"):
        Settings()
