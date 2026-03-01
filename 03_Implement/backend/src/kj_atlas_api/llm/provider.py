from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol
from urllib import error, request
from uuid import uuid4

from kj_atlas_api.settings import settings


@dataclass(frozen=True)
class LLMRequest:
    task: str
    prompt: str
    temperature: float = 0.2
    max_tokens: int = 2000


@dataclass(frozen=True)
class LLMCallMetadata:
    provider_kind: str
    provider_name: str
    model_id: str
    transport: str
    requested_at: str
    trace_id: str
    fallback_to_none: bool = False


@dataclass(frozen=True)
class LLMResponse:
    raw_text: str
    metadata: LLMCallMetadata

    @property
    def provider(self) -> str:
        return self.metadata.provider_name

    @property
    def transport(self) -> str:
        return self.metadata.transport

    @property
    def trace_id(self) -> str:
        return self.metadata.trace_id


class LLMProvider(Protocol):
    provider_name: str
    provider_kind: str

    def generate(self, req: LLMRequest) -> LLMResponse:
        ...


class ProviderError(RuntimeError):
    def __init__(self, message: str, metadata: LLMCallMetadata):
        super().__init__(message)
        self.metadata = metadata


class ProviderDisabledError(ProviderError):
    pass


class ProviderRequestError(ProviderError):
    pass


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_metadata(*, provider_kind: str, provider_name: str, model_id: str, transport: str, fallback_to_none: bool = False) -> LLMCallMetadata:
    return LLMCallMetadata(
        provider_kind=provider_kind,
        provider_name=provider_name,
        model_id=model_id,
        transport=transport,
        requested_at=_now_utc_iso(),
        trace_id=f"llm-{uuid4()}",
        fallback_to_none=fallback_to_none,
    )


class NoneProvider:
    provider_name = "none"
    provider_kind = "none"

    def generate(self, req: LLMRequest) -> LLMResponse:
        metadata = _new_metadata(
            provider_kind=self.provider_kind,
            provider_name=self.provider_name,
            model_id="none",
            transport="none",
        )
        raise ProviderDisabledError(
            "AI is disabled. Set LLM_PROVIDER to local or large-scale.",
            metadata,
        )


class LocalProvider:
    provider_name = "local"
    provider_kind = "local"

    def generate(self, req: LLMRequest) -> LLMResponse:
        base_url = settings.local_llm_base_url
        model_id = settings.local_llm_model or "unknown"
        metadata = _new_metadata(
            provider_kind=self.provider_kind,
            provider_name=self.provider_name,
            model_id=model_id,
            transport="http",
        )

        if not base_url:
            raise ProviderRequestError("LOCAL_LLM_BASE_URL is not set", metadata)

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
            raise ProviderRequestError(f"Local LLM request failed with status {exc.code}", metadata) from exc
        except error.URLError as exc:
            raise ProviderRequestError(f"Local LLM request failed: {exc.reason}", metadata) from exc

        try:
            body = json.loads(raw_body)
        except json.JSONDecodeError as exc:
            raise ProviderRequestError("Local LLM response was not valid JSON", metadata) from exc

        text = body.get("text")
        if not isinstance(text, str):
            raise ProviderRequestError("Local LLM response missing text field", metadata)

        return LLMResponse(raw_text=text, metadata=metadata)


class LargeScaleProvider:
    provider_name = "large-scale"
    provider_kind = "large-scale"

    def generate(self, req: LLMRequest) -> LLMResponse:
        model_id = settings.large_scale_llm_model or "unknown"
        metadata = _new_metadata(
            provider_kind=self.provider_kind,
            provider_name=self.provider_name,
            model_id=model_id,
            transport="http",
        )

        if not settings.large_scale_llm_base_url:
            raise ProviderRequestError("LARGE_SCALE_LLM_BASE_URL is not set", metadata)
        if not settings.large_scale_llm_model:
            raise ProviderRequestError("LARGE_SCALE_LLM_MODEL is not set", metadata)

        raise ProviderRequestError("Large-scale LLM provider is not implemented", metadata)


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

    metadata = _new_metadata(
        provider_kind="unknown",
        provider_name=normalized or "unknown",
        model_id="unknown",
        transport="none",
    )
    raise ProviderRequestError(f"Unsupported LLM_PROVIDER: {settings.llm_provider}", metadata)


def generate_with_fallback(req: LLMRequest) -> LLMResponse:
    provider = get_provider()
    try:
        return provider.generate(req)
    except ProviderRequestError as exc:
        if not settings.llm_fallback_to_none:
            raise
        fallback_metadata = LLMCallMetadata(
            provider_kind="none",
            provider_name="none",
            model_id="none",
            transport="none",
            requested_at=_now_utc_iso(),
            trace_id=exc.metadata.trace_id,
            fallback_to_none=True,
        )
        raise ProviderDisabledError(
            f"LLM provider '{exc.metadata.provider_name}' failed and fallbacked to none: {exc}",
            fallback_metadata,
        ) from exc
