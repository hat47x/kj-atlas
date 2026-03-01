from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Protocol
from urllib import error, request
from uuid import uuid4

from kj_atlas_api.settings import settings


@dataclass
class LLMRequest:
    task: str
    prompt: str
    temperature: float = 0.2
    max_tokens: int = 2000


@dataclass
class LLMResponse:
    raw_text: str
    provider: str
    transport: str
    trace_id: str


class LLMProvider(Protocol):
    provider_name: str

    def generate(self, req: LLMRequest) -> LLMResponse:
        ...


class ProviderDisabledError(RuntimeError):
    pass


class ProviderRequestError(RuntimeError):
    pass


class NoneProvider:
    provider_name = "none"

    def generate(self, req: LLMRequest) -> LLMResponse:
        raise ProviderDisabledError("AI is disabled. Set LLM_PROVIDER to local or large-scale.")


class LocalProvider:
    provider_name = "local"

    def generate(self, req: LLMRequest) -> LLMResponse:
        base_url = settings.local_llm_base_url
        if not base_url:
            raise ProviderRequestError("LOCAL_LLM_BASE_URL is not set")

        endpoint = f"{base_url.rstrip('/')}/generate"
        payload = {
            "task": req.task,
            "prompt": req.prompt,
            "temperature": req.temperature,
            "max_tokens": req.max_tokens,
            "model": settings.local_llm_model,
        }

        req_obj = request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with request.urlopen(req_obj, timeout=60) as resp:
                raw_body = resp.read().decode("utf-8")
        except error.HTTPError as exc:
            raise ProviderRequestError(f"Local LLM request failed with status {exc.code}") from exc
        except error.URLError as exc:
            raise ProviderRequestError(f"Local LLM request failed: {exc.reason}") from exc

        try:
            body = json.loads(raw_body)
        except json.JSONDecodeError as exc:
            raise ProviderRequestError("Local LLM response was not valid JSON") from exc

        text = body.get("text")
        if not isinstance(text, str):
            raise ProviderRequestError("Local LLM response missing text field")

        return LLMResponse(
            raw_text=text,
            provider=self.provider_name,
            transport="http",
            trace_id=f"llm-{uuid4()}",
        )


class LargeScaleProvider:
    provider_name = "large-scale"

    def generate(self, req: LLMRequest) -> LLMResponse:
        if not settings.large_scale_llm_base_url:
            raise ProviderRequestError("LARGE_SCALE_LLM_BASE_URL is not set")
        if not settings.large_scale_llm_model:
            raise ProviderRequestError("LARGE_SCALE_LLM_MODEL is not set")

        raise ProviderRequestError("Large-scale LLM provider is not implemented")


_PROVIDER_ALIASES = {
    "none": "none",
    "local": "local",
    "local_http": "local",
    "large-scale": "large-scale",
    "large_scale": "large-scale",
    "external": "large-scale",
}


def get_provider() -> LLMProvider:
    normalized = settings.llm_provider.lower().strip()
    provider_name = _PROVIDER_ALIASES.get(normalized)

    if provider_name == "none":
        return NoneProvider()
    if provider_name == "local":
        return LocalProvider()
    if provider_name == "large-scale":
        return LargeScaleProvider()

    raise ProviderRequestError(f"Unsupported LLM_PROVIDER: {settings.llm_provider}")
