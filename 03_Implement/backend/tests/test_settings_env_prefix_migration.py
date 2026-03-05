from __future__ import annotations

import os

from kj_atlas_api.settings import Settings


LEGACY_ENV_KEYS = {
    "DATABASE_URL",
    "LLM_PROVIDER",
    "LOCAL_LLM_BASE_URL",
    "LOCAL_LLM_MODEL",
    "LARGE_SCALE_LLM_BASE_URL",
    "LARGE_SCALE_LLM_MODEL",
    "LLM_ESCALATION_ENABLED",
    "LLM_LARGE_SCALE_OPT_IN",
    "LARGE_SCALE_LLM_ALLOWLIST",
    "LLM_FALLBACK_TO_NONE",
    "API_KEY",
    "AUDIT_EXPORT_ENABLED",
    "AUDIT_TRANSPORT",
    "AUDIT_HTTP_ENDPOINT",
    "AUDIT_HTTP_API_KEY",
    "AUDIT_HTTP_TIMEOUT_SECONDS",
    "AUDIT_QUEUE_SIZE",
    "AUDIT_ALLOW_IN_SAFE_MODE",
    "ACCESS_CONTROL_ADAPTER",
    "ACCESS_CONTROL_FAIL_SAFE_MODE",
    "ACCESS_CONTROL_EXTERNAL_HTTP_ENDPOINT",
    "ACCESS_CONTROL_EXTERNAL_HTTP_TIMEOUT_SECONDS",
    "ACCESS_CONTROL_EXTERNAL_HTTP_AUTH_MODE",
    "ACCESS_CONTROL_EXTERNAL_HTTP_STATIC_BEARER_TOKEN",
    "ACCESS_CONTROL_EXTERNAL_HTTP_IDP_ISSUER",
    "ALLOW_JIT_PROVISIONING",
    "AUTH_PROVIDER_FIELD",
    "AUTH_USER_FIELD",
    "AUTH_EMAIL_FIELD",
    "AUTH_NAME_FIELD",
    "AUTH_SUBJECT_FIELD",
    "REVIEWER_REF_RESOLVER_ADAPTER",
}


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
