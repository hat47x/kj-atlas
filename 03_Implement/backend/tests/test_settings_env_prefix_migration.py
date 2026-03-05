from __future__ import annotations

import os

from kj_atlas_api.settings import Settings


def _unset_related_envs() -> None:
    for key in list(os.environ):
        if key.startswith("KJ_ATLAS_"):
            os.environ.pop(key, None)
    os.environ.pop("DATABASE_URL", None)


def test_settings_accepts_legacy_key_for_backward_compatibility(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    _unset_related_envs()
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./legacy.db")

    loaded = Settings()

    assert loaded.database_url == "sqlite:///./legacy.db"


def test_settings_prefers_prefixed_key_when_both_set(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    _unset_related_envs()
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./legacy.db")
    monkeypatch.setenv("KJ_ATLAS_DATABASE_URL", "sqlite:///./canonical.db")

    loaded = Settings()

    assert loaded.database_url == "sqlite:///./canonical.db"
