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


def test_settings_rejects_legacy_key_only(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    _unset_related_envs()
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./legacy.db")

    try:
        Settings()
        assert False, "Expected legacy-only env to be rejected"
    except ValueError as exc:
        assert "Legacy env keys are no longer supported" in str(exc)
        assert "DATABASE_URL" in str(exc)


def test_settings_rejects_mixed_prefixed_and_legacy_keys(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    _unset_related_envs()
    monkeypatch.setenv("KJ_ATLAS_DATABASE_URL", "sqlite:///./canonical.db")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./legacy.db")

    try:
        Settings()
        assert False, "Expected mixed env keys to be rejected"
    except ValueError as exc:
        assert "Legacy env keys are no longer supported" in str(exc)
        assert "DATABASE_URL" in str(exc)


def test_settings_normalizes_access_control_auth_mode(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    _unset_related_envs()
    monkeypatch.setenv("KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_AUTH_MODE", "  OIDC ")

    loaded = Settings()

    assert loaded.access_control_external_http_auth_mode == "oidc"


def test_settings_normalizes_reviewer_ref_resolver_adapter(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    _unset_related_envs()
    monkeypatch.setenv("KJ_ATLAS_REVIEWER_REF_RESOLVER_ADAPTER", "  SSO_SUBJECT ")

    loaded = Settings()

    assert loaded.reviewer_ref_resolver_adapter == "sso_subject"
