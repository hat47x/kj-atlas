from __future__ import annotations

import pytest

from kj_atlas_api.settings import Settings


def _large_scale_settings(**overrides: object) -> dict[str, object]:
    configured: dict[str, object] = {
        "KJ_ATLAS_LLM_PROVIDER": "large-scale",
        "KJ_ATLAS_LLM_ESCALATION_ENABLED": True,
        "KJ_ATLAS_LLM_LARGE_SCALE_OPT_IN": True,
        "KJ_ATLAS_LARGE_SCALE_LLM_BASE_URL": "https://llm.example.invalid/v1",
        "KJ_ATLAS_LARGE_SCALE_LLM_MODEL": "model-v1",
        "KJ_ATLAS_LARGE_SCALE_LLM_ALLOWLIST": "llm.example.invalid",
    }
    configured.update(overrides)
    return configured


@pytest.mark.parametrize(
    "settings_overrides",
    [
        {"KJ_ATLAS_LOCAL_LLM_BASE_URL": "http://127.0.0.1:8001/v1"},
        {"KJ_ATLAS_LOCAL_LLM_BASE_URL": "https://llm.intranet.invalid/v1"},
        _large_scale_settings(),
    ],
)
def test_llm_settings_accept_trusted_http_destinations(
    settings_overrides: dict[str, object],
) -> None:
    configured = Settings(**settings_overrides)

    assert configured.local_llm_base_url or configured.large_scale_llm_base_url


@pytest.mark.parametrize(
    "endpoint",
    [
        "http://llm.example.invalid/v1",
        "https://user:password@llm.example.invalid/v1",
        "https://llm.example.invalid/v1?token=secret",
        "https://llm.example.invalid/v1?",
        "https://llm.example.invalid/v1#fragment",
        "https://llm.example.invalid/v1#",
        "https://llm.example.invalid:invalid/v1",
        " https://llm.example.invalid/v1",
        "https://llm.example.invalid\\@other.invalid/v1",
    ],
)
def test_llm_settings_reject_untrusted_endpoint_shapes_without_reflection(
    endpoint: str,
) -> None:
    with pytest.raises(ValueError) as exc_info:
        Settings(KJ_ATLAS_LOCAL_LLM_BASE_URL=endpoint)

    assert "password" not in str(exc_info.value)
    assert "secret" not in str(exc_info.value)


@pytest.mark.parametrize(
    "missing_key",
    [
        "KJ_ATLAS_LARGE_SCALE_LLM_BASE_URL",
        "KJ_ATLAS_LARGE_SCALE_LLM_MODEL",
        "KJ_ATLAS_LARGE_SCALE_LLM_ALLOWLIST",
    ],
)
def test_large_scale_provider_requires_complete_destination_settings(
    missing_key: str,
) -> None:
    configured = _large_scale_settings()
    configured.pop(missing_key)

    with pytest.raises(ValueError, match="requires its base URL, model, and allowlist"):
        Settings(**configured)


@pytest.mark.parametrize(
    "allowlist",
    [
        "",
        "*.example.invalid",
        "https://llm.example.invalid",
        "llm.example.invalid:443",
        "llm.example.invalid/path",
        "user@llm.example.invalid",
        "llm.example.invalid,,other.example.invalid",
        "llm.example.invalid,LLM.EXAMPLE.INVALID",
        "ｌｌｍ.example.invalid",
    ],
)
def test_large_scale_allowlist_rejects_noncanonical_or_duplicate_hosts(
    allowlist: str,
) -> None:
    with pytest.raises(ValueError):
        Settings(
            **_large_scale_settings(
                KJ_ATLAS_LARGE_SCALE_LLM_ALLOWLIST=allowlist,
            )
        )


def test_large_scale_provider_requires_base_host_in_allowlist() -> None:
    with pytest.raises(ValueError, match="BASE_URL host must be in"):
        Settings(
            **_large_scale_settings(
                KJ_ATLAS_LARGE_SCALE_LLM_ALLOWLIST="other.example.invalid",
            )
        )


def test_large_scale_allowlist_is_normalized() -> None:
    configured = Settings(
        **_large_scale_settings(
            KJ_ATLAS_LARGE_SCALE_LLM_ALLOWLIST=(
                "LLM.EXAMPLE.INVALID, backup.example.invalid"
            ),
        )
    )

    assert configured.large_scale_llm_allowlist == (
        "llm.example.invalid,backup.example.invalid"
    )


@pytest.mark.parametrize(
    "model_id",
    ["", " model-v1", "model v1", "model\\v1", "model\nv1", "x" * 257],
)
def test_llm_settings_reject_noncanonical_model_identifiers(model_id: str) -> None:
    with pytest.raises(ValueError) as exc_info:
        Settings(KJ_ATLAS_LOCAL_LLM_MODEL=model_id)

    if model_id:
        assert model_id not in str(exc_info.value)
