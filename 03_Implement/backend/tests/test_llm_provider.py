from __future__ import annotations

import io
import json
from urllib import error

import pytest

from kj_atlas_api.llm.provider import (
    LLMRequest,
    LargeScaleProvider,
    LocalProvider,
    NoneProvider,
    ProviderDisabledError,
    ProviderRequestError,
    get_provider,
)
from kj_atlas_api.main import app
from kj_atlas_api.settings import settings


class _StubHTTPResponse:
    def __init__(self, body: str):
        self._buffer = io.BytesIO(body.encode("utf-8"))

    def read(self) -> bytes:
        return self._buffer.read()

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

    def _fake_urlopen(req, timeout=60):
        assert req.full_url == "http://local-llm.test/generate"
        payload = json.loads(req.data.decode("utf-8"))
        assert payload["model"] == "test-model"
        return _StubHTTPResponse('{"text":"ok"}')

    monkeypatch.setattr("kj_atlas_api.llm.provider.request.urlopen", _fake_urlopen)

    try:
        response = LocalProvider().generate(LLMRequest(task="check_narrative", prompt="prompt"))
        assert response.raw_text == "ok"
        assert response.provider == "local"
        assert response.transport == "http"
        assert response.trace_id.startswith("llm-")
    finally:
        settings.local_llm_base_url = original_url
        settings.local_llm_model = original_model


def test_local_provider_handles_http_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    original_url = settings.local_llm_base_url
    settings.local_llm_base_url = "http://local-llm.test"

    def _fake_urlopen(req, timeout=60):
        raise error.URLError("offline")

    monkeypatch.setattr("kj_atlas_api.llm.provider.request.urlopen", _fake_urlopen)

    try:
        with pytest.raises(ProviderRequestError):
            LocalProvider().generate(LLMRequest(task="check_narrative", prompt="prompt"))
    finally:
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


def test_api_does_not_expose_decision_finalization_routes() -> None:
    forbidden_paths = {"/ai/decision", "/ai/decisions", "/ai/finalize-decision", "/ai/confirm-decision"}
    defined_paths = {route.path for route in app.routes}
    assert forbidden_paths.isdisjoint(defined_paths)
