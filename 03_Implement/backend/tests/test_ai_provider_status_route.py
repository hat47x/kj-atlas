from fastapi.testclient import TestClient

from kj_atlas_api.main import app
from kj_atlas_api.settings import settings


def test_provider_status_echoes_none_by_default() -> None:
    original_api_key = settings.api_key
    original_provider = settings.llm_provider

    settings.api_key = None
    settings.llm_provider = "none"

    try:
        with TestClient(app) as client:
            response = client.get("/ai/provider-status")
        assert response.status_code == 200
        assert response.json() == {"providerKind": "none"}
    finally:
        settings.api_key = original_api_key
        settings.llm_provider = original_provider


def test_provider_status_echoes_local_and_resolves_alias() -> None:
    original_api_key = settings.api_key
    original_provider = settings.llm_provider

    settings.api_key = None
    settings.llm_provider = "local_http"

    try:
        with TestClient(app) as client:
            response = client.get("/ai/provider-status")
        assert response.status_code == 200
        # PROV-VIS-01: the resolved provider_kind is returned, not the raw alias.
        assert response.json() == {"providerKind": "local"}
    finally:
        settings.api_key = original_api_key
        settings.llm_provider = original_provider


def test_provider_status_is_a_static_config_echo_not_a_connectivity_check() -> None:
    """PROV-VIS-01 (ADR-0050 D1): this endpoint must not attempt to reach the
    configured local/large-scale endpoint. Setting local provider with no
    reachable base URL must still return 200 (echo only)."""
    original_api_key = settings.api_key
    original_provider = settings.llm_provider
    original_base_url = settings.local_llm_base_url

    settings.api_key = None
    settings.llm_provider = "local"
    settings.local_llm_base_url = None

    try:
        with TestClient(app) as client:
            response = client.get("/ai/provider-status")
        assert response.status_code == 200
        assert response.json() == {"providerKind": "local"}
    finally:
        settings.api_key = original_api_key
        settings.llm_provider = original_provider
        settings.local_llm_base_url = original_base_url
