from __future__ import annotations

import os

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


def test_settings_ignores_legacy_key(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    _unset_related_envs()
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./legacy.db")

    loaded = Settings()

    assert loaded.database_url == "sqlite:///./kj_atlas.db"


def test_settings_prefers_prefixed_key_over_legacy_key(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    _unset_related_envs()
    monkeypatch.setenv("KJ_ATLAS_DATABASE_URL", "sqlite:///./canonical.db")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./legacy.db")

    loaded = Settings()

    assert loaded.database_url == "sqlite:///./canonical.db"
