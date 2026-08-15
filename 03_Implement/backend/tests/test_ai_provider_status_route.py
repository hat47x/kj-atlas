from fastapi.testclient import TestClient

from kj_atlas_api.llm.provider import reset_llm_call_counts
from kj_atlas_api.main import app
from kj_atlas_api.settings import settings


def test_provider_status_echoes_none_by_default() -> None:
    original_api_key = settings.api_key
    original_provider = settings.llm_provider
    reset_llm_call_counts()

    settings.api_key = None
    settings.llm_provider = "none"

    try:
        with TestClient(app) as client:
            response = client.get("/ai/provider-status")
        assert response.status_code == 200
        assert response.json() == {"providerKind": "none", "callCounts": {}}
    finally:
        settings.api_key = original_api_key
        settings.llm_provider = original_provider


def test_provider_status_echoes_local_and_resolves_alias() -> None:
    original_api_key = settings.api_key
    original_provider = settings.llm_provider
    reset_llm_call_counts()

    settings.api_key = None
    settings.llm_provider = "local_http"

    try:
        with TestClient(app) as client:
            response = client.get("/ai/provider-status")
        assert response.status_code == 200
        # PROV-VIS-01: the resolved provider_kind is returned, not the raw alias.
        assert response.json() == {"providerKind": "local", "callCounts": {}}
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
    reset_llm_call_counts()

    settings.api_key = None
    settings.llm_provider = "local"
    settings.local_llm_base_url = None

    try:
        with TestClient(app) as client:
            response = client.get("/ai/provider-status")
        assert response.status_code == 200
        assert response.json() == {"providerKind": "local", "callCounts": {}}
    finally:
        settings.api_key = original_api_key
        settings.llm_provider = original_provider
        settings.local_llm_base_url = original_base_url


def test_provider_status_reports_llm_call_counts_after_a_call(monkeypatch) -> None:
    """OPS-LLM-COST-01 (段階2): a real generate_with_fallback increments the
    in-process counter, referenceable via /ai/provider-status."""
    from kj_atlas_api.llm import provider as llm_provider
    from kj_atlas_api.routes import ai as ai_routes

    class _StubResponse:
        raw_text = '{"refinedText": "（モック）改善案", "reasoning": "r"}'

    class _StubProvider:
        provider_kind = "large-scale"
        provider_name = "stub"

        def generate(self, _req):
            return _StubResponse()

    # generate_with_fallback (defined in llm/provider.py) resolves the provider
    # via its OWN module-level get_provider; the provider-status route resolves
    # it via its imported reference. Patch both to the stub.
    monkeypatch.setattr(llm_provider, "get_provider", lambda: _StubProvider())
    monkeypatch.setattr(ai_routes, "get_provider", lambda: _StubProvider())
    reset_llm_call_counts()

    with TestClient(app) as client:
        resp = client.post("/ai/refine-card-text", json={"cardText": "alpha", "textReviewed": True})
        assert resp.status_code == 200, resp.text
        status = client.get("/ai/provider-status")
        body = status.json()
    assert body["providerKind"] == "large-scale"
    assert body["callCounts"].get("large-scale") == 1
    assert body["callCounts"].get("total") == 1
