from __future__ import annotations

import json
import logging
import math
import re
import socket
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urlparse
from typing import Callable, Literal, Protocol
from urllib import error, request
from uuid import uuid4

from kj_atlas_api.settings import settings
from kj_atlas_api.trusted_http import open_trusted_http

logger = logging.getLogger(__name__)

MAX_LLM_PROVIDER_REQUEST_BYTES = 1024 * 1024
MAX_LLM_PROVIDER_RESPONSE_BYTES = 1024 * 1024
MAX_LLM_TASK_LENGTH = 128
MAX_LLM_OUTPUT_TOKENS = 32_768
_LLM_TASK = re.compile(r"^[a-z][a-z0-9_-]{0,127}$")


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
    execution_path: str = "primary"

    def as_audit_fields(self) -> dict[str, object]:
        return {
            "provider": self.provider_name,
            "provider_kind": self.provider_kind,
            "model_id": self.model_id,
            "transport": self.transport,
            "requested_at": self.requested_at,
            "fallback_to_none": self.fallback_to_none,
            "execution_path": self.execution_path,
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
            "model_id": self.metadata.model_id,
            "transport": self.metadata.transport,
            "requested_at": self.metadata.requested_at,
            "trace_id": self.metadata.trace_id,
            "fallback_to_none": self.metadata.fallback_to_none,
            "execution_path": self.metadata.execution_path,
        }


class ProviderDisabledError(ProviderError):
    def to_contract(self) -> dict[str, object]:
        base = super().to_contract()
        base["disabled_reason"] = "provider_disabled_or_none_default"
        return base


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
            "model_id": self.metadata.model_id,
            "transport": self.metadata.transport,
            "requested_at": self.metadata.requested_at,
            "trace_id": self.metadata.trace_id,
            "fallback_to_none": self.metadata.fallback_to_none,
            "execution_path": self.metadata.execution_path,
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
            "AI is disabled. Set KJ_ATLAS_LLM_PROVIDER to local or large-scale.",
            metadata,
        )


class LocalProvider:
    provider_name = "local"
    provider_kind = "local"

    def generate(self, req: LLMRequest) -> LLMResponse:
        return _generate_via_http(
            req,
            base_url=settings.local_llm_base_url,
            model_id=settings.local_llm_model,
            provider_kind=self.provider_kind,
            provider_name=self.provider_name,
            missing_base_url_message="KJ_ATLAS_LOCAL_LLM_BASE_URL is not set",
            missing_model_message=None,
        )


class LargeScaleProvider:
    provider_name = "large-scale"
    provider_kind = "large-scale"

    def generate(self, req: LLMRequest) -> LLMResponse:
        if not settings.llm_large_scale_opt_in:
            metadata = _new_metadata(
                provider_kind=self.provider_kind,
                provider_name=self.provider_name,
                model_id=settings.large_scale_llm_model or "unknown",
                transport="http",
            )
            raise ProviderRequestError.unavailable("Large-scale provider requires explicit opt-in", metadata)

        if not settings.llm_escalation_enabled:
            metadata = _new_metadata(
                provider_kind=self.provider_kind,
                provider_name=self.provider_name,
                model_id=settings.large_scale_llm_model or "unknown",
                transport="http",
            )
            raise ProviderRequestError.unavailable("Large-scale provider disabled by local-first policy", metadata)

        _ensure_large_scale_allowlist()
        return _generate_via_http(
            req,
            base_url=settings.large_scale_llm_base_url,
            model_id=settings.large_scale_llm_model,
            provider_kind=self.provider_kind,
            provider_name=self.provider_name,
            missing_base_url_message="KJ_ATLAS_LARGE_SCALE_LLM_BASE_URL is not set",
            missing_model_message="KJ_ATLAS_LARGE_SCALE_LLM_MODEL is not set",
        )


def _normalize_allowlist(raw_allowlist: str | None) -> set[str]:
    if not raw_allowlist:
        return set()
    return {item.strip().lower() for item in raw_allowlist.split(",") if item.strip()}


def _ensure_large_scale_allowlist() -> None:
    base_url = settings.large_scale_llm_base_url
    allowlist = _normalize_allowlist(settings.large_scale_llm_allowlist)
    metadata = _new_metadata(
        provider_kind="large-scale",
        provider_name="large-scale",
        model_id=settings.large_scale_llm_model or "unknown",
        transport="http",
    )

    if not base_url:
        raise ProviderRequestError.unavailable("KJ_ATLAS_LARGE_SCALE_LLM_BASE_URL is not set", metadata)

    hostname = (urlparse(base_url).hostname or "").lower()
    if hostname == "":
        raise ProviderRequestError.validation("KJ_ATLAS_LARGE_SCALE_LLM_BASE_URL is invalid", metadata)
    if hostname not in allowlist:
        raise ProviderRequestError.unavailable("Large-scale destination is not allowlisted", metadata)


def _parse_http_provider_response(
    response_body: bytes,
    *,
    provider_name: str,
    metadata: LLMCallMetadata,
) -> str:
    if len(response_body) > MAX_LLM_PROVIDER_RESPONSE_BYTES:
        raise ProviderRequestError.validation(
            f"{provider_name} response exceeded the size limit",
            metadata,
        )
    try:
        body = json.loads(response_body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ProviderRequestError.validation(
            f"{provider_name} response was not valid JSON",
            metadata,
        ) from None
    if not isinstance(body, dict) or set(body) != {"text"}:
        raise ProviderRequestError.validation(
            f"{provider_name} response had an invalid shape",
            metadata,
        )
    text = body["text"]
    if not isinstance(text, str):
        raise ProviderRequestError.validation(
            f"{provider_name} response missing text field",
            metadata,
        )
    return text


def _serialize_http_provider_request(
    req: LLMRequest,
    *,
    model_id: str | None,
    provider_name: str,
    metadata: LLMCallMetadata,
) -> bytes:
    if (
        not isinstance(req.task, str)
        or len(req.task) > MAX_LLM_TASK_LENGTH
        or not _LLM_TASK.fullmatch(req.task)
    ):
        raise ProviderRequestError.validation(
            f"{provider_name} request had an invalid task",
            metadata,
        )
    if not isinstance(req.prompt, str) or not req.prompt:
        raise ProviderRequestError.validation(
            f"{provider_name} request had an invalid prompt",
            metadata,
        )
    if (
        not isinstance(req.temperature, (int, float))
        or isinstance(req.temperature, bool)
        or not math.isfinite(req.temperature)
        or not 0 <= req.temperature <= 2
        or not isinstance(req.max_tokens, int)
        or isinstance(req.max_tokens, bool)
        or not 1 <= req.max_tokens <= MAX_LLM_OUTPUT_TOKENS
    ):
        raise ProviderRequestError.validation(
            f"{provider_name} request had invalid generation parameters",
            metadata,
        )
    try:
        serialized = json.dumps(
            {
                "task": req.task,
                "prompt": req.prompt,
                "temperature": req.temperature,
                "max_tokens": req.max_tokens,
                "model": model_id,
            },
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError):
        raise ProviderRequestError.validation(
            f"{provider_name} request could not be serialized",
            metadata,
        ) from None
    if len(serialized) > MAX_LLM_PROVIDER_REQUEST_BYTES:
        raise ProviderRequestError.validation(
            f"{provider_name} request exceeded the size limit",
            metadata,
        )
    return serialized


def _generate_via_http(
    req: LLMRequest,
    *,
    base_url: str | None,
    model_id: str | None,
    provider_kind: str,
    provider_name: str,
    missing_base_url_message: str,
    missing_model_message: str | None,
) -> LLMResponse:
    resolved_model = model_id or "unknown"
    metadata = _new_metadata(
        provider_kind=provider_kind,
        provider_name=provider_name,
        model_id=resolved_model,
        transport="http",
    )

    if not base_url:
        raise ProviderRequestError.unavailable(missing_base_url_message, metadata)
    if missing_model_message is not None and not model_id:
        raise ProviderRequestError.unavailable(missing_model_message, metadata)

    endpoint = f"{base_url.rstrip('/')}/generate"
    payload = _serialize_http_provider_request(
        req,
        model_id=model_id,
        provider_name=provider_name,
        metadata=metadata,
    )
    req_obj = request.Request(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with open_trusted_http(req_obj, timeout_seconds=60) as resp:
            response_body = resp.read(MAX_LLM_PROVIDER_RESPONSE_BYTES + 1)
    except error.HTTPError as exc:
        if exc.code in (408, 504):
            raise ProviderRequestError.timeout(f"{provider_name} request timed out with status {exc.code}", metadata) from exc
        raise ProviderRequestError.unavailable(f"{provider_name} request failed with status {exc.code}", metadata) from exc
    except error.URLError as exc:
        reason = exc.reason
        if isinstance(reason, socket.timeout):
            raise ProviderRequestError.timeout(f"{provider_name} request timed out", metadata) from exc
        logger.warning("%s request failed: %s", provider_name, reason, exc_info=True)
        raise ProviderRequestError.unavailable(f"{provider_name} request failed", metadata) from exc
    except TimeoutError as exc:
        raise ProviderRequestError.timeout(
            f"{provider_name} request timed out",
            metadata,
        ) from exc
    except OSError as exc:
        raise ProviderRequestError.unavailable(
            f"{provider_name} request failed",
            metadata,
        ) from exc

    text = _parse_http_provider_response(
        response_body,
        provider_name=provider_name,
        metadata=metadata,
    )
    return LLMResponse(raw_text=text, metadata=metadata)


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
            raise ProviderRequestError.unavailable(f"Unsupported KJ_ATLAS_LLM_PROVIDER: {raw_provider_name}", metadata)
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
        "execution_path": getattr(metadata, "execution_path", "primary"),
        "trace_id": getattr(llm_response, "trace_id", getattr(metadata, "trace_id", "unknown")),
    }


def get_provider() -> LLMProvider:
    return _DEFAULT_REGISTRY.resolve(settings.llm_provider)


def generate_with_fallback(req: LLMRequest) -> LLMResponse:
    provider = get_provider()
    try:
        return provider.generate(req)
    except ProviderRequestError as exc:
        if exc.code == "provider_validation" or not settings.llm_fallback_to_none:
            raise
        fallback_metadata = LLMCallMetadata(
            provider_kind="none",
            provider_name="none",
            model_id="none",
            transport="none",
            requested_at=_now_utc_iso(),
            trace_id=exc.metadata.trace_id,
            fallback_to_none=True,
            execution_path=f"{exc.metadata.provider_name}->none",
        )
        raise ProviderDisabledError(
            f"LLM provider '{exc.metadata.provider_name}' failed ({exc.code}) and fallbacked to none",
            fallback_metadata,
        ) from exc
