from __future__ import annotations

import json
import re
from dataclasses import dataclass
from urllib import error as urllib_error
from urllib import request as urllib_request

from sqlalchemy.orm import Session

from kj_atlas_api.session_context import (
    KNOWN_EFFECTIVE_CAPABILITIES,
    CapabilitySnapshot,
    TenantCapabilityResolver,
)
from kj_atlas_api.settings import settings
from kj_atlas_api.tenant_context import TenantContext
from kj_atlas_api.trusted_http import open_trusted_http


MAX_CAPABILITY_REQUEST_BYTES = 64 * 1024
MAX_CAPABILITY_RESPONSE_BYTES = 64 * 1024
MAX_CAPABILITY_COUNT = len(KNOWN_EFFECTIVE_CAPABILITIES)
_OPAQUE_VERSION = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


class TenantCapabilityUnavailableError(RuntimeError):
    """The trusted capability source could not be used."""


class TenantCapabilityInvalidResponseError(ValueError):
    """The trusted capability source returned an invalid snapshot."""


@dataclass(frozen=True, slots=True)
class ExternalTenantCapabilityConfig:
    endpoint: str
    timeout_seconds: float = 1.5
    api_key: str | None = None


def _canonical_request_identifier(value: str | None) -> str:
    if (
        value is None
        or not value
        or len(value) > 256
        or value.strip() != value
        or any(not character.isprintable() for character in value)
    ):
        raise TenantCapabilityUnavailableError("tenant capability context is unavailable")
    return value


def _serialize_capability_request(
    *,
    principal_id: str,
    tenant: TenantContext,
) -> bytes:
    try:
        body = json.dumps(
            {
                "principalId": _canonical_request_identifier(principal_id),
                "tenantId": _canonical_request_identifier(tenant.tenant_id),
                "membershipId": _canonical_request_identifier(tenant.membership_id),
            },
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError, UnicodeError):
        raise TenantCapabilityUnavailableError(
            "tenant capability context is unavailable"
        ) from None
    if len(body) > MAX_CAPABILITY_REQUEST_BYTES:
        raise TenantCapabilityUnavailableError(
            "tenant capability context is unavailable"
        )
    return body


def _parse_snapshot(response_body: bytes) -> CapabilitySnapshot:
    if len(response_body) > MAX_CAPABILITY_RESPONSE_BYTES:
        raise TenantCapabilityInvalidResponseError(
            "capability service response exceeds the size limit"
        )
    try:
        decoded = json.loads(response_body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise TenantCapabilityInvalidResponseError(
            "capability service response is not valid JSON"
        ) from None
    if not isinstance(decoded, dict) or set(decoded) != {
        "effectiveCapabilities",
        "capabilityVersion",
    }:
        raise TenantCapabilityInvalidResponseError(
            "capability service response has an invalid shape"
        )

    raw_capabilities = decoded["effectiveCapabilities"]
    capability_version = decoded["capabilityVersion"]
    if (
        not isinstance(raw_capabilities, list)
        or len(raw_capabilities) > MAX_CAPABILITY_COUNT
        or any(not isinstance(capability, str) for capability in raw_capabilities)
        or len(set(raw_capabilities)) != len(raw_capabilities)
        or any(capability not in KNOWN_EFFECTIVE_CAPABILITIES for capability in raw_capabilities)
    ):
        raise TenantCapabilityInvalidResponseError(
            "capability service returned an invalid capability set"
        )
    if not isinstance(capability_version, str) or not _OPAQUE_VERSION.fullmatch(
        capability_version
    ):
        raise TenantCapabilityInvalidResponseError(
            "capability service returned an invalid capability version"
        )
    return CapabilitySnapshot(
        effective_capabilities=tuple(raw_capabilities),
        capability_version=capability_version,
    )


class ExternalHttpTenantCapabilityResolver:
    """Resolve tenant capabilities from a trusted policy service."""

    def __init__(self, *, config: ExternalTenantCapabilityConfig) -> None:
        self._config = config

    def resolve(
        self,
        *,
        db: Session,  # noqa: ARG002
        principal_id: str,
        tenant: TenantContext,
    ) -> CapabilitySnapshot:
        body = _serialize_capability_request(
            principal_id=principal_id,
            tenant=tenant,
        )
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
        }
        if self._config.api_key is not None:
            headers["authorization"] = f"Bearer {self._config.api_key}"
        outbound = urllib_request.Request(
            self._config.endpoint,
            data=body,
            headers=headers,
            method="POST",
        )
        try:
            with open_trusted_http(
                outbound,
                timeout_seconds=self._config.timeout_seconds,
            ) as response:
                response_body = response.read(MAX_CAPABILITY_RESPONSE_BYTES + 1)
        except urllib_error.HTTPError as exc:
            if exc.code in {400, 401, 403, 404, 409, 422}:
                raise TenantCapabilityInvalidResponseError(
                    "capability service rejected the lookup"
                ) from None
            raise TenantCapabilityUnavailableError(
                "capability service is unavailable"
            ) from None
        except (urllib_error.URLError, TimeoutError, OSError):
            raise TenantCapabilityUnavailableError(
                "capability service is unavailable"
            ) from None
        return _parse_snapshot(response_body)


class UnavailableTenantCapabilityResolver:
    def resolve(
        self,
        *,
        db: Session,  # noqa: ARG002
        principal_id: str,  # noqa: ARG002
        tenant: TenantContext,  # noqa: ARG002
    ) -> CapabilitySnapshot:
        raise TenantCapabilityUnavailableError("capability service is unavailable")


def build_tenant_capability_resolver() -> TenantCapabilityResolver:
    if settings.tenant_capability_resolver != "external_http":
        return UnavailableTenantCapabilityResolver()
    endpoint = settings.tenant_capability_http_endpoint
    if endpoint is None:
        return UnavailableTenantCapabilityResolver()
    return ExternalHttpTenantCapabilityResolver(
        config=ExternalTenantCapabilityConfig(
            endpoint=endpoint,
            timeout_seconds=settings.tenant_capability_http_timeout_seconds,
            api_key=settings.tenant_capability_http_api_key,
        )
    )
