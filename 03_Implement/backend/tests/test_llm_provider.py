from __future__ import annotations

import io
import json
import socket
from urllib import error

import pytest
from fastapi.testclient import TestClient

from kj_atlas_api.llm.provider import (
    LLMRequest,
    LLMCallMetadata,
    LLMResponse,
    LargeScaleProvider,
    LocalProvider,
    MAX_LLM_PROVIDER_RESPONSE_BYTES,
    NoOpProvider,
    NoneProvider,
    ProviderDisabledError,
    ProviderRequestError,
    generate_with_fallback,
    get_provider,
)
from kj_atlas_api.main import app
from kj_atlas_api.settings import Settings, settings


class _StubHTTPResponse:
    def __init__(self, body: str | bytes):
        self._buffer = io.BytesIO(
            body.encode("utf-8") if isinstance(body, str) else body
        )

    def read(self, size: int = -1) -> bytes:
        return self._buffer.read(size)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_get_provider_supports_none_local_and_large_scale() -> None:
    original = settings.llm_provider
    try:
        settings.llm_provider = "none"
        assert isinstance(get_provider(), NoneProvider)

        settings.llm_provider = "local"
        assert isinstance(get_provider(), LocalProvider)

        settings.llm_provider = "large-scale"
        assert isinstance(get_provider(), LargeScaleProvider)
    finally:
        settings.llm_provider = original


@pytest.mark.parametrize(
    ("provider_name", "expected_type"),
    [
        ("local_http", LocalProvider),
        ("external", LargeScaleProvider),
    ],
)
def test_get_provider_backward_compatible_aliases(provider_name: str, expected_type: type) -> None:
    original = settings.llm_provider
    try:
        settings.llm_provider = provider_name
        assert isinstance(get_provider(), expected_type)
    finally:
        settings.llm_provider = original


def test_none_provider_is_disabled() -> None:
    provider = NoneProvider()
    with pytest.raises(ProviderDisabledError):
        provider.generate(LLMRequest(task="x", prompt="y"))


def test_local_provider_returns_trace_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    original_url = settings.local_llm_base_url
    original_model = settings.local_llm_model
    settings.local_llm_base_url = "http://local-llm.test"
    settings.local_llm_model = "test-model"

    def _fake_urlopen(req, timeout_seconds=60):
        assert req.full_url == "http://local-llm.test/generate"
        payload = json.loads(req.data.decode("utf-8"))
        assert payload["model"] == "test-model"
        return _StubHTTPResponse('{"text":"ok"}')

    monkeypatch.setattr("kj_atlas_api.llm.provider.open_trusted_http", _fake_urlopen)

    try:
        response = LocalProvider().generate(LLMRequest(task="check_narrative", prompt="prompt"))
        assert response.raw_text == "ok"
        assert response.provider == "local"
        assert response.metadata.provider_kind == "local"
        assert response.metadata.model_id == "test-model"
        assert response.transport == "http"
        assert response.trace_id.startswith("llm-")
        assert response.metadata.requested_at
    finally:
        settings.local_llm_base_url = original_url
        settings.local_llm_model = original_model


def test_local_provider_handles_http_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    original_url = settings.local_llm_base_url
    settings.local_llm_base_url = "http://local-llm.test"

    def _fake_urlopen(req, timeout_seconds=60):
        raise error.URLError("offline")

    monkeypatch.setattr("kj_atlas_api.llm.provider.open_trusted_http", _fake_urlopen)

    try:
        with pytest.raises(ProviderRequestError):
            LocalProvider().generate(LLMRequest(task="check_narrative", prompt="prompt"))
    finally:
        settings.local_llm_base_url = original_url



def test_local_provider_maps_timeout_error_code(monkeypatch: pytest.MonkeyPatch) -> None:
    original_url = settings.local_llm_base_url
    settings.local_llm_base_url = "http://local-llm.test"

    def _fake_urlopen(req, timeout_seconds=60):
        raise error.URLError(socket.timeout("timed out"))

    monkeypatch.setattr("kj_atlas_api.llm.provider.open_trusted_http", _fake_urlopen)

    try:
        with pytest.raises(ProviderRequestError) as exc_info:
            LocalProvider().generate(LLMRequest(task="check_narrative", prompt="prompt"))
        assert exc_info.value.code == "provider_timeout"
    finally:
        settings.local_llm_base_url = original_url


def test_local_provider_maps_validation_error_code(monkeypatch: pytest.MonkeyPatch) -> None:
    original_url = settings.local_llm_base_url
    settings.local_llm_base_url = "http://local-llm.test"

    def _fake_urlopen(req, timeout_seconds=60):
        return _StubHTTPResponse('{"text":123}')

    monkeypatch.setattr("kj_atlas_api.llm.provider.open_trusted_http", _fake_urlopen)

    try:
        with pytest.raises(ProviderRequestError) as exc_info:
            LocalProvider().generate(LLMRequest(task="check_narrative", prompt="prompt"))
        assert exc_info.value.code == "provider_validation"
    finally:
        settings.local_llm_base_url = original_url


@pytest.mark.parametrize(
    "response_body",
    [
        b"[]",
        b'{"text":"ok","token":"response-secret"}',
        b"\xff",
        b"x" * (MAX_LLM_PROVIDER_RESPONSE_BYTES + 1),
    ],
    ids=["array", "extra-field", "invalid-utf8", "oversized"],
)
def test_local_provider_rejects_unbounded_or_noncanonical_response_without_reflection(
    monkeypatch: pytest.MonkeyPatch,
    response_body: bytes,
) -> None:
    original_url = settings.local_llm_base_url
    settings.local_llm_base_url = "http://local-llm.test"
    monkeypatch.setattr(
        "kj_atlas_api.llm.provider.open_trusted_http",
        lambda request, timeout_seconds: _StubHTTPResponse(response_body),  # noqa: ARG005
    )
    try:
        with pytest.raises(ProviderRequestError) as exc_info:
            LocalProvider().generate(
                LLMRequest(task="check_narrative", prompt="tenant prompt")
            )
        assert exc_info.value.code == "provider_validation"
        assert "response-secret" not in str(exc_info.value)
    finally:
        settings.local_llm_base_url = original_url

def test_generate_with_fallback_to_none_when_enabled() -> None:
    original_provider = settings.llm_provider
    original_fallback = settings.llm_fallback_to_none
    original_url = settings.local_llm_base_url
    settings.llm_provider = "local"
    settings.llm_fallback_to_none = True
    settings.local_llm_base_url = None

    try:
        with pytest.raises(ProviderDisabledError) as exc_info:
            generate_with_fallback(LLMRequest(task="check_narrative", prompt="prompt"))
        assert exc_info.value.metadata.provider_name == "none"
        assert exc_info.value.metadata.fallback_to_none is True
        assert exc_info.value.metadata.execution_path == "local->none"
    finally:
        settings.llm_provider = original_provider
        settings.llm_fallback_to_none = original_fallback
        settings.local_llm_base_url = original_url


def test_generate_with_fallback_keeps_original_error_when_disabled() -> None:
    original_provider = settings.llm_provider
    original_fallback = settings.llm_fallback_to_none
    original_url = settings.local_llm_base_url
    settings.llm_provider = "local"
    settings.llm_fallback_to_none = False
    settings.local_llm_base_url = None

    try:
        with pytest.raises(ProviderRequestError):
            generate_with_fallback(LLMRequest(task="check_narrative", prompt="prompt"))
    finally:
        settings.llm_provider = original_provider
        settings.llm_fallback_to_none = original_fallback
        settings.local_llm_base_url = original_url


def test_large_scale_provider_fails_closed_without_endpoint() -> None:
    original_base_url = settings.large_scale_llm_base_url
    original_model = settings.large_scale_llm_model
    settings.large_scale_llm_base_url = None
    settings.large_scale_llm_model = None

    try:
        with pytest.raises(ProviderRequestError):
            LargeScaleProvider().generate(LLMRequest(task="generate_narrative", prompt="prompt"))
    finally:
        settings.large_scale_llm_base_url = original_base_url
        settings.large_scale_llm_model = original_model


def test_large_scale_provider_requires_escalation_opt_in() -> None:
    original_enabled = settings.llm_escalation_enabled
    original_opt_in = settings.llm_large_scale_opt_in
    original_base_url = settings.large_scale_llm_base_url
    original_model = settings.large_scale_llm_model

    settings.llm_large_scale_opt_in = True
    settings.llm_escalation_enabled = False
    settings.large_scale_llm_base_url = "https://allowed.example/api"
    settings.large_scale_llm_model = "gpt-x"

    try:
        with pytest.raises(ProviderRequestError) as exc_info:
            LargeScaleProvider().generate(LLMRequest(task="generate_narrative", prompt="prompt"))
        assert exc_info.value.code == "provider_unavailable"
    finally:
        settings.llm_escalation_enabled = original_enabled
        settings.llm_large_scale_opt_in = original_opt_in
        settings.large_scale_llm_base_url = original_base_url
        settings.large_scale_llm_model = original_model


def test_large_scale_provider_rejects_non_allowlisted_destination() -> None:
    original_enabled = settings.llm_escalation_enabled
    original_opt_in = settings.llm_large_scale_opt_in
    original_base_url = settings.large_scale_llm_base_url
    original_model = settings.large_scale_llm_model
    original_allowlist = settings.large_scale_llm_allowlist

    settings.llm_large_scale_opt_in = True
    settings.llm_escalation_enabled = True
    settings.large_scale_llm_base_url = "https://blocked.example/api"
    settings.large_scale_llm_model = "gpt-x"
    settings.large_scale_llm_allowlist = "allowed.example"

    try:
        with pytest.raises(ProviderRequestError) as exc_info:
            LargeScaleProvider().generate(LLMRequest(task="generate_narrative", prompt="prompt"))
        assert exc_info.value.code == "provider_unavailable"
    finally:
        settings.llm_escalation_enabled = original_enabled
        settings.llm_large_scale_opt_in = original_opt_in
        settings.large_scale_llm_base_url = original_base_url
        settings.large_scale_llm_model = original_model
        settings.large_scale_llm_allowlist = original_allowlist


def test_api_does_not_expose_decision_finalization_routes() -> None:
    forbidden_paths = {"/ai/decision", "/ai/decisions", "/ai/finalize-decision", "/ai/confirm-decision"}
    defined_paths = {route.path for route in app.routes}
    assert forbidden_paths.isdisjoint(defined_paths)


def test_suggest_merges_contract_is_stable_across_provider_switch(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = {
        "doc": {
            "version": 1,
            "id": "doc-1",
            "createdAt": "2026-02-11T00:00:00Z",
            "updatedAt": "2026-02-11T00:00:00Z",
            "transform": {"panX": 0, "panY": 0, "zoom": 1},
            "cards": [
                {"id": "c1", "text": "alpha", "x": 0, "y": 0},
                {"id": "c2", "text": "beta", "x": 10, "y": 10},
            ],
            "edges": [{"id": "e1", "fromId": "c1", "toId": "c2", "type": "related"}],
            "islands": [{"id": "i1", "cardIds": ["c1", "c2"]}],
        }
    }

    original_api_key = settings.api_key
    original_provider = settings.llm_provider
    original_local_url = settings.local_llm_base_url
    original_local_model = settings.local_llm_model
    original_escalation = settings.llm_escalation_enabled
    original_opt_in = settings.llm_large_scale_opt_in
    original_allowlist = settings.large_scale_llm_allowlist
    original_large_url = settings.large_scale_llm_base_url
    original_large_model = settings.large_scale_llm_model

    def _fake_local_urlopen(req, timeout_seconds=60):
        body = json.dumps(
            {
                "text": '{"suggestions":[{"groupId":"g1","cardIds":["c1","c2"],"mergedTextDraft":"merged"}]}'
            }
        )
        return _StubHTTPResponse(body)

    def _fake_large_scale_generate(self, req: LLMRequest) -> LLMResponse:
        return LLMResponse(
            raw_text='{"suggestions":[{"groupId":"g1","cardIds":["c1","c2"],"mergedTextDraft":"merged"}]}',
            metadata=LLMCallMetadata(
                provider_kind="large-scale",
                provider_name="large-scale",
                model_id="mock-large",
                transport="mock",
                requested_at="2026-01-01T00:00:00+00:00",
                trace_id="llm-test",
            ),
        )

    monkeypatch.setattr("kj_atlas_api.llm.provider.open_trusted_http", _fake_local_urlopen)
    monkeypatch.setattr("kj_atlas_api.llm.provider.LargeScaleProvider.generate", _fake_large_scale_generate)

    try:
        settings.api_key = None
        settings.local_llm_base_url = "http://local-llm.test"
        settings.local_llm_model = "local-model"

        with TestClient(app) as client:
            settings.llm_provider = "local"
            local_response = client.post("/ai/suggest-merges", json=payload)
            assert local_response.status_code == 200

            settings.llm_provider = "large-scale"
            settings.llm_large_scale_opt_in = True
            settings.llm_escalation_enabled = True
            settings.large_scale_llm_allowlist = "allowed.example"
            settings.large_scale_llm_base_url = "https://allowed.example/api"
            settings.large_scale_llm_model = "mock-large"
            large_response = client.post("/ai/suggest-merges", json=payload)
            assert large_response.status_code == 200

        assert local_response.json() == large_response.json()
        assert list(local_response.json().keys()) == ["suggestions"]
    finally:
        settings.api_key = original_api_key
        settings.llm_provider = original_provider
        settings.local_llm_base_url = original_local_url
        settings.local_llm_model = original_local_model
        settings.llm_escalation_enabled = original_escalation
        settings.llm_large_scale_opt_in = original_opt_in
        settings.large_scale_llm_allowlist = original_allowlist
        settings.large_scale_llm_base_url = original_large_url
        settings.large_scale_llm_model = original_large_model


def test_default_registry_maps_none_to_noop_provider() -> None:
    original = settings.llm_provider
    try:
        settings.llm_provider = "none"
        assert isinstance(get_provider(), NoOpProvider)
    finally:
        settings.llm_provider = original


def test_response_audit_fields_include_provider_and_execution_metadata() -> None:
    metadata = LLMCallMetadata(
        provider_kind="local",
        provider_name="local",
        model_id="model-a",
        transport="http",
        requested_at="2026-01-01T00:00:00+00:00",
        trace_id="llm-trace",
        fallback_to_none=False,
    )
    response = LLMResponse(raw_text="{}", metadata=metadata)

    assert response.as_audit_fields() == {
        "provider": "local",
        "provider_kind": "local",
        "model_id": "model-a",
        "transport": "http",
        "requested_at": "2026-01-01T00:00:00+00:00",
        "fallback_to_none": False,
        "execution_path": "primary",
        "trace_id": "llm-trace",
    }


def test_provider_error_contract_mapping_is_consistent() -> None:
    metadata = LLMCallMetadata(
        provider_kind="local",
        provider_name="local",
        model_id="model-a",
        transport="http",
        requested_at="2026-01-01T00:00:00+00:00",
        trace_id="llm-trace",
        fallback_to_none=False,
    )
    timeout_error = ProviderRequestError.timeout("timeout", metadata)
    validation_error = ProviderRequestError.validation("invalid", metadata)
    unavailable_error = ProviderRequestError.unavailable("down", metadata)

    assert timeout_error.to_contract()["code"] == "provider_timeout"
    assert validation_error.to_contract()["code"] == "provider_validation"
    assert unavailable_error.to_contract()["code"] == "provider_unavailable"


def test_settings_reject_large_scale_without_explicit_opt_in(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KJ_ATLAS_LLM_PROVIDER", "large-scale")
    monkeypatch.setenv("KJ_ATLAS_LLM_ESCALATION_ENABLED", "true")

    with pytest.raises(ValueError, match="KJ_ATLAS_LLM_LARGE_SCALE_OPT_IN"):
        Settings()


def test_settings_accept_large_scale_with_opt_in_and_escalation(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KJ_ATLAS_LLM_PROVIDER", "large-scale")
    monkeypatch.setenv("KJ_ATLAS_LLM_LARGE_SCALE_OPT_IN", "true")
    monkeypatch.setenv("KJ_ATLAS_LLM_ESCALATION_ENABLED", "true")
    monkeypatch.setenv(
        "KJ_ATLAS_LARGE_SCALE_LLM_BASE_URL",
        "https://llm.example.invalid/v1",
    )
    monkeypatch.setenv("KJ_ATLAS_LARGE_SCALE_LLM_MODEL", "model-v1")
    monkeypatch.setenv("KJ_ATLAS_LARGE_SCALE_LLM_ALLOWLIST", "llm.example.invalid")

    loaded = Settings()
    assert loaded.llm_provider == "large-scale"
    assert loaded.llm_large_scale_opt_in is True
    assert loaded.llm_escalation_enabled is True
