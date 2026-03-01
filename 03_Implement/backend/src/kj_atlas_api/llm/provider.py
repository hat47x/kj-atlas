from __future__ import annotations

import json
import socket
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Literal, Protocol
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

    def as_audit_fields(self) -> dict[str, object]:
        return {
            "provider": self.provider_name,
            "provider_kind": self.provider_kind,
            "model_id": self.model_id,
            "transport": self.transport,
            "requested_at": self.requested_at,
            "fallback_to_none": self.fallback_to_none,
            "trace_id": self.trace_id,
        }


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

    def as_audit_fields(self) -> dict[str, object]:
        return self.metadata.as_audit_fields()


class LLMProvider(Protocol):
    provider_name: str
    provider_kind: str

    def generate(self, req: LLMRequest) -> LLMResponse:
        ...


class ProviderError(RuntimeError):
    def __init__(self, message: str, metadata: LLMCallMetadata):
        super().__init__(message)
        self.metadata = metadata

    def to_contract(self) -> dict[str, object]:
        return {
            "code": "provider_unavailable",
            "message": str(self),
            "provider": self.metadata.provider_name,
            "provider_kind": self.metadata.provider_kind,
            "trace_id": self.metadata.trace_id,
            "fallback_to_none": self.metadata.fallback_to_none,
        }


class ProviderDisabledError(ProviderError):
    pass


ProviderErrorCode = Literal["provider_timeout", "provider_validation", "provider_unavailable"]


class ProviderRequestError(ProviderError):
    def __init__(self, message: str, metadata: LLMCallMetadata, *, code: ProviderErrorCode):
        super().__init__(message, metadata)
        self.code = code

    def to_contract(self) -> dict[str, object]:
        return {
            "code": self.code,
            "message": str(self),
            "provider": self.metadata.provider_name,
            "provider_kind": self.metadata.provider_kind,
            "trace_id": self.metadata.trace_id,
            "fallback_to_none": self.metadata.fallback_to_none,
        }

    @classmethod
    def unavailable(cls, message: str, metadata: LLMCallMetadata) -> "ProviderRequestError":
        return cls(message, metadata, code="provider_unavailable")

    @classmethod
    def timeout(cls, message: str, metadata: LLMCallMetadata) -> "ProviderRequestError":
        return cls(message, metadata, code="provider_timeout")

    @classmethod
    def validation(cls, message: str, metadata: LLMCallMetadata) -> "ProviderRequestError":
        return cls(message, metadata, code="provider_validation")


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
            raise ProviderRequestError.unavailable("LOCAL_LLM_BASE_URL is not set", metadata)

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
            if exc.code in (408, 504):
                raise ProviderRequestError.timeout(f"Local LLM request timed out with status {exc.code}", metadata) from exc
            raise ProviderRequestError.unavailable(f"Local LLM request failed with status {exc.code}", metadata) from exc
        except error.URLError as exc:
            reason = exc.reason
            if isinstance(reason, socket.timeout):
                raise ProviderRequestError.timeout("Local LLM request timed out", metadata) from exc
            raise ProviderRequestError.unavailable(f"Local LLM request failed: {reason}", metadata) from exc

        try:
            body = json.loads(raw_body)
        except json.JSONDecodeError as exc:
            raise ProviderRequestError.validation("Local LLM response was not valid JSON", metadata) from exc

        text = body.get("text")
        if not isinstance(text, str):
            raise ProviderRequestError.validation("Local LLM response missing text field", metadata)

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
            raise ProviderRequestError.unavailable("LARGE_SCALE_LLM_BASE_URL is not set", metadata)
        if not settings.large_scale_llm_model:
            raise ProviderRequestError.unavailable("LARGE_SCALE_LLM_MODEL is not set", metadata)

        raise ProviderRequestError.unavailable("Large-scale LLM provider is not implemented", metadata)


class NoOpProvider(NoneProvider):
    """Explicit no-op provider for adapter registry wiring."""


ProviderFactory = Callable[[], LLMProvider]


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, ProviderFactory] = {}
        self._aliases: dict[str, str] = {}

    def register(self, provider_name: str, factory: ProviderFactory, *, aliases: tuple[str, ...] = ()) -> None:
        normalized_name = provider_name.lower().strip()
        self._providers[normalized_name] = factory
        self._aliases[normalized_name] = normalized_name
        for alias in aliases:
            self._aliases[alias.lower().strip()] = normalized_name

    def resolve(self, raw_provider_name: str) -> LLMProvider:
        normalized = raw_provider_name.lower().strip()
        provider_name = self._aliases.get(normalized)
        if provider_name is None:
            metadata = _new_metadata(
                provider_kind="unknown",
                provider_name=normalized or "unknown",
                model_id="unknown",
                transport="none",
            )
            raise ProviderRequestError.unavailable(f"Unsupported LLM_PROVIDER: {raw_provider_name}", metadata)
        return self._providers[provider_name]()


def _build_default_registry() -> ProviderRegistry:
    registry = ProviderRegistry()
    registry.register("none", NoOpProvider)
    registry.register("local", LocalProvider, aliases=("local_http",))
    registry.register("large-scale", LargeScaleProvider, aliases=("large_scale", "external"))
    return registry


_DEFAULT_REGISTRY = _build_default_registry()




def build_audit_fields(llm_response: object) -> dict[str, object]:
    if hasattr(llm_response, "as_audit_fields"):
        return getattr(llm_response, "as_audit_fields")()

    metadata = getattr(llm_response, "metadata", None)
    return {
        "provider": getattr(llm_response, "provider", getattr(metadata, "provider_name", "unknown")),
        "provider_kind": getattr(metadata, "provider_kind", "unknown"),
        "model_id": getattr(metadata, "model_id", "unknown"),
        "transport": getattr(llm_response, "transport", getattr(metadata, "transport", "unknown")),
        "requested_at": getattr(metadata, "requested_at", "unknown"),
        "fallback_to_none": getattr(metadata, "fallback_to_none", False),
        "trace_id": getattr(llm_response, "trace_id", getattr(metadata, "trace_id", "unknown")),
    }


def get_provider() -> LLMProvider:
    return _DEFAULT_REGISTRY.resolve(settings.llm_provider)


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
