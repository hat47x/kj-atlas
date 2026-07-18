from __future__ import annotations

import json
from dataclasses import dataclass
from urllib import error as urllib_error
from urllib import request as urllib_request

from kj_atlas_api.document_access_resource import (
    DocumentPolicyBindingResolver,
    UnavailableDocumentPolicyBindingResolver,
)
from kj_atlas_api.settings import settings
from kj_atlas_api.tenant_context import TenantContext
from kj_atlas_api.trusted_http import open_trusted_http


MAX_BINDING_REQUEST_BYTES = 64 * 1024
MAX_BINDING_RESPONSE_BYTES = 64 * 1024
MAX_BINDING_TENANT_ID_LENGTH = 256
MAX_BINDING_LOOKUP_ID_LENGTH = 128
MAX_POLICY_REF_LENGTH = 2048


class DocumentPolicyBindingUnavailableError(RuntimeError):
    """The trusted binding service could not be reached."""


class DocumentPolicyBindingInvalidResponseError(ValueError):
    """The trusted binding service returned an unusable response."""


@dataclass(frozen=True, slots=True)
class ExternalDocumentPolicyBindingConfig:
    endpoint: str
    timeout_seconds: float = 1.5
    api_key: str | None = None


def _canonical_policy_ref(value: object) -> str:
    if (
        not isinstance(value, str)
        or not value
        or len(value) > MAX_POLICY_REF_LENGTH
        or value.strip() != value
        or any(not character.isprintable() for character in value)
    ):
        raise DocumentPolicyBindingInvalidResponseError(
            "binding service returned an invalid policy reference"
        )
    return value


def _canonical_lookup_identifier(value: object, *, max_length: int) -> str:
    if (
        not isinstance(value, str)
        or not value
        or len(value) > max_length
        or value.strip() != value
        or any(not character.isprintable() for character in value)
    ):
        raise DocumentPolicyBindingUnavailableError(
            "binding service lookup context is unavailable"
        )
    return value


def _serialize_binding_lookup(
    *,
    tenant: TenantContext,
    binding_id: str,
    policy_version: str,
) -> bytes:
    try:
        body = json.dumps(
            {
                "tenantId": _canonical_lookup_identifier(
                    tenant.tenant_id,
                    max_length=MAX_BINDING_TENANT_ID_LENGTH,
                ),
                "bindingId": _canonical_lookup_identifier(
                    binding_id,
                    max_length=MAX_BINDING_LOOKUP_ID_LENGTH,
                ),
                "policyVersion": _canonical_lookup_identifier(
                    policy_version,
                    max_length=MAX_BINDING_LOOKUP_ID_LENGTH,
                ),
            },
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError, UnicodeError):
        raise DocumentPolicyBindingUnavailableError(
            "binding service lookup context is unavailable"
        ) from None
    if len(body) > MAX_BINDING_REQUEST_BYTES:
        raise DocumentPolicyBindingUnavailableError(
            "binding service lookup context is unavailable"
        )
    return body


class ExternalHttpDocumentPolicyBindingResolver:
    """Resolve an opaque binding ID without persisting or logging raw policy refs."""

    def __init__(self, *, config: ExternalDocumentPolicyBindingConfig) -> None:
        self._config = config

    def resolve(
        self,
        *,
        tenant: TenantContext,
        binding_id: str,
        policy_version: str,
    ) -> str | None:
        body = _serialize_binding_lookup(
            tenant=tenant,
            binding_id=binding_id,
            policy_version=policy_version,
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
                response_body = response.read(MAX_BINDING_RESPONSE_BYTES + 1)
        except urllib_error.HTTPError as exc:
            if exc.code in {400, 401, 403, 404, 409, 422}:
                raise DocumentPolicyBindingInvalidResponseError(
                    "binding service rejected the lookup"
                ) from None
            raise DocumentPolicyBindingUnavailableError(
                "binding service is unavailable"
            ) from None
        except (urllib_error.URLError, TimeoutError, OSError):
            raise DocumentPolicyBindingUnavailableError(
                "binding service is unavailable"
            ) from None

        if len(response_body) > MAX_BINDING_RESPONSE_BYTES:
            raise DocumentPolicyBindingInvalidResponseError(
                "binding service response exceeds the size limit"
            )
        try:
            decoded = json.loads(response_body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise DocumentPolicyBindingInvalidResponseError(
                "binding service response is not valid JSON"
            ) from None
        if not isinstance(decoded, dict) or set(decoded) != {"policyRef"}:
            raise DocumentPolicyBindingInvalidResponseError(
                "binding service response must contain only policyRef"
            )
        return _canonical_policy_ref(decoded["policyRef"])


def build_document_policy_binding_resolver() -> DocumentPolicyBindingResolver:
    if settings.document_policy_binding_resolver != "external_http":
        return UnavailableDocumentPolicyBindingResolver()
    endpoint = settings.document_policy_binding_http_endpoint
    if endpoint is None:
        return UnavailableDocumentPolicyBindingResolver()
    return ExternalHttpDocumentPolicyBindingResolver(
        config=ExternalDocumentPolicyBindingConfig(
            endpoint=endpoint,
            timeout_seconds=settings.document_policy_binding_http_timeout_seconds,
            api_key=settings.document_policy_binding_http_api_key,
        )
    )
