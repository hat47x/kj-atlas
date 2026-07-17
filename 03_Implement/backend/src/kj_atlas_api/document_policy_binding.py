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


MAX_BINDING_RESPONSE_BYTES = 64 * 1024
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
        or any(ord(character) < 32 or ord(character) == 127 for character in value)
    ):
        raise DocumentPolicyBindingInvalidResponseError(
            "binding service returned an invalid policy reference"
        )
    return value


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
        body = json.dumps(
            {
                "tenantId": tenant.tenant_id,
                "bindingId": binding_id,
                "policyVersion": policy_version,
            },
            separators=(",", ":"),
        ).encode("utf-8")
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
            with urllib_request.urlopen(  # noqa: S310
                outbound,
                timeout=self._config.timeout_seconds,
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
