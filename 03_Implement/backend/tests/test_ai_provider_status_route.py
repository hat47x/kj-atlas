import pytest
from fastapi.testclient import TestClient

from kj_atlas_api.llm.provider import reset_llm_call_counts
from kj_atlas_api.main import app
from kj_atlas_api.settings import settings


@pytest.fixture(scope="module", autouse=True)
def _app_db_schema() -> None:
    """Ensure the shared SQLite DB has the full app schema AND a registered
    provider/model matching the generation tests' stubbed runtime provider
    (large-scale). _assert_model_allowed (AI-MODEL-GOVERNANCE-02) requires an
    active registered model whose provider matches the runtime; a fresh SQLite
    DB has neither until seeded."""
    from sqlalchemy.exc import IntegrityError

    from kj_atlas_api.db import SessionLocal, engine
    from kj_atlas_api.models import Base
    from kj_atlas_api.model_registry_repository import register_model, register_provider

    _NOW = "2026-08-15T00:00:00+00:00"
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        register_provider(
            db,
            provider_id="large-scale",
            provider_kind="large-scale",
            display_name="Large-scale LLM (test)",
            base_url=None,
            api_key_ref=None,
            occurred_at=_NOW,
        )
        register_model(
            db,
            model_id="default",
            provider_id="large-scale",
            display_name="default",
            capabilities="intermediate,generate",
            occurred_at=_NOW,
        )
        db.commit()
    except IntegrityError:
        db.rollback()
    finally:
        db.close()


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
        assert response.json() == {"providerKind": "none", "callCounts": {}, "tokenUsage": {}}
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
        assert response.json() == {"providerKind": "local", "callCounts": {}, "tokenUsage": {}}
    finally:
        settings.api_key = original_api_key
        settings.llm_provider = original_provider


def test_provider_status_echoes_deepseek() -> None:
    original_api_key = settings.api_key
    original_provider = settings.llm_provider
    original_deepseek_key = settings.deepseek_api_key
    reset_llm_call_counts()

    settings.api_key = None
    settings.llm_provider = "deepseek"
    settings.deepseek_api_key = "test-only-key"

    try:
        with TestClient(app) as client:
            response = client.get("/ai/provider-status")
        assert response.status_code == 200
        assert response.json() == {"providerKind": "deepseek", "callCounts": {}, "tokenUsage": {}}
    finally:
        settings.api_key = original_api_key
        settings.llm_provider = original_provider
        settings.deepseek_api_key = original_deepseek_key


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
        assert response.json() == {"providerKind": "local", "callCounts": {}, "tokenUsage": {}}
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
        input_tokens = None
        output_tokens = None

    class _StubProvider:
        provider_kind = "large-scale"
        provider_name = "stub"

        def generate(self, _req):
            return _StubResponse()

    # generate_with_fallback (defined in llm/provider.py) resolves the provider
    # via its OWN module-level get_provider; the provider-status route resolves
    # it via its imported reference. Patch both to the stub. This test is about
    # call/token accounting, not model governance, so bypass the allowlist gate.
    monkeypatch.setattr(llm_provider, "get_provider", lambda: _StubProvider())
    monkeypatch.setattr(ai_routes, "get_provider", lambda: _StubProvider())
    monkeypatch.setattr(ai_routes, "_assert_model_allowed", lambda *a, **k: None)
    reset_llm_call_counts()

    with TestClient(app) as client:
        resp = client.post("/ai/refine-card-text", json={"cardText": "alpha", "textReviewed": True})
        assert resp.status_code == 200, resp.text
        status = client.get("/ai/provider-status")
        body = status.json()
    assert body["providerKind"] == "large-scale"
    assert body["callCounts"].get("large-scale") == 1
    assert body["callCounts"].get("total") == 1
    # No provider-reported usage -> 0 tokens recorded for the call.
    assert body["tokenUsage"] == {
        "large-scale": {"input": 0, "output": 0},
        "total": {"input": 0, "output": 0},
    }


def test_provider_status_reports_token_usage_from_provider_response(monkeypatch) -> None:
    """OPS-LLM-COST-01 (段階2): provider-reported input/output tokens are
    accumulated per provider kind and exposed via /ai/provider-status."""
    from kj_atlas_api.llm import provider as llm_provider
    from kj_atlas_api.routes import ai as ai_routes

    class _StubResponse:
        raw_text = '{"refinedText": "（モック）改善案", "reasoning": "r"}'
        input_tokens = 120
        output_tokens = 37

    class _StubProvider:
        provider_kind = "large-scale"
        provider_name = "stub"

        def generate(self, _req):
            return _StubResponse()

    monkeypatch.setattr(llm_provider, "get_provider", lambda: _StubProvider())
    monkeypatch.setattr(ai_routes, "get_provider", lambda: _StubProvider())
    # This test is about token accounting, not model governance; bypass the gate.
    monkeypatch.setattr(ai_routes, "_assert_model_allowed", lambda *a, **k: None)
    reset_llm_call_counts()

    with TestClient(app) as client:
        resp = client.post("/ai/refine-card-text", json={"cardText": "alpha", "textReviewed": True})
        assert resp.status_code == 200, resp.text
        resp2 = client.post("/ai/refine-card-text", json={"cardText": "beta", "textReviewed": True})
        assert resp2.status_code == 200, resp2.text
        body = client.get("/ai/provider-status").json()

    assert body["callCounts"].get("large-scale") == 2
    assert body["tokenUsage"]["large-scale"] == {"input": 240, "output": 74}
    assert body["tokenUsage"]["total"] == {"input": 240, "output": 74}
