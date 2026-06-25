from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Literal, Protocol, cast
from urllib import error as urllib_error
from urllib import request as urllib_request

from fastapi import HTTPException

AccessAction = Literal["read", "write", "export", "share"]
Visibility = Literal["Public", "Unlisted", "Org", "Restricted"]
FailSafeMode = Literal["deny", "read_only"]
FailSafeReason = Literal[
    "safe_mode",
    "read_only",
    "policy_ref_missing",
    "policy_ref_unreachable",
    "policy_ref_invalid",
    "adapter_error",
]


@dataclass(frozen=True)
class AuthContext:
    actor_ref: str | None
    user_id: str | None = None
    provider: str | None = None
    external_uid: str | None = None
    roles: tuple[str, ...] = ()
    groups: tuple[str, ...] = ()
    trace_id: str | None = None
    amr: str | None = None
    acr: str | None = None
    aal: str | None = None
    auth_time: str | None = None


@dataclass(frozen=True)
class AccessSubject:
    """Public API alias for AuthContext-compatible subject reference."""
    actor_ref: str | None = None
    roles: tuple[str, ...] = ()
    groups: tuple[str, ...] = ()


@dataclass(frozen=True)
class AccessResource:
    doc_id: str
    visibility: Visibility | None = None
    policy_ref: str | None = None


@dataclass(frozen=True)
class AccessRequest:
    action: AccessAction
    auth: AuthContext
    resource: AccessResource
    safe_mode: bool
    read_only: bool


@dataclass(frozen=True)
class AccessDecision:
    allow: bool
    read_only: bool = False
    reason: FailSafeReason | str | None = None


class AccessControlAdapter(Protocol):
    """Externalized authorization adapter contract.

    The adapter can call external RBAC/ABAC engines. Application core must not
    embed role/group/policy evaluation logic.
    """

    name: str

    def authorize(self, request: AccessRequest) -> AccessDecision:
        ...


class AccessControlUnreachableError(RuntimeError):
    """External policy endpoint is unreachable (timeout/DNS/network)."""


class AccessControlInvalidPolicyError(ValueError):
    """Policy ref is invalid/expired/failed verification."""


class NoopAccessControlAdapter:
    name = "noop"

    def authorize(self, request: AccessRequest) -> AccessDecision:  # noqa: ARG002
        return AccessDecision(allow=True)


class MockAccessControlAdapter:
    """Deterministic adapter for contract/integration tests.

    This adapter is intentionally simple and only exists to validate the
    AccessControlAdapter I/F wiring. Production RBAC/ABAC logic must remain
    external.
    """

    name = "mock"

    def authorize(self, request: AccessRequest) -> AccessDecision:
        token = request.resource.policy_ref
        if token == "mock:deny":
            return AccessDecision(allow=False, reason="mock_deny")
        if token == "mock:read_only":
            return AccessDecision(allow=True, read_only=True, reason="mock_read_only")
        return AccessDecision(allow=True)


AdapterAuthMode = Literal["none", "oidc", "saml"]


@dataclass(frozen=True)
class ExternalPolicyAdapterConfig:
    endpoint: str
    timeout_seconds: float = 1.5
    auth_mode: AdapterAuthMode = "none"
    static_bearer_token: str | None = None
    idp_issuer: str | None = None


class ExternalPolicyAccessControlAdapter:
    """HTTP bridge to enterprise policy engines behind OIDC/SAML SSO.

    RBAC/ABAC evaluation remains external; this adapter only forwards
    AccessRequest and validates the AccessDecision contract.
    """

    name = "external_http"

    def __init__(self, *, config: ExternalPolicyAdapterConfig):
        self._config = config

    def authorize(self, request: AccessRequest) -> AccessDecision:
        auth_payload: dict[str, object] = {
            "actorRef": request.auth.actor_ref,
            "roles": list(request.auth.roles),
            "groups": list(request.auth.groups),
            "traceId": request.auth.trace_id,
        }
        if request.auth.user_id is not None:
            auth_payload["userId"] = request.auth.user_id
        if request.auth.provider is not None:
            auth_payload["provider"] = request.auth.provider
        if request.auth.external_uid is not None:
            auth_payload["externalUid"] = request.auth.external_uid
        if request.auth.amr is not None:
            auth_payload["amr"] = request.auth.amr
        if request.auth.acr is not None:
            auth_payload["acr"] = request.auth.acr
        if request.auth.aal is not None:
            auth_payload["aal"] = request.auth.aal
        if request.auth.auth_time is not None:
            auth_payload["authTime"] = request.auth.auth_time

        payload = {
            "action": request.action,
            "auth": auth_payload,
            "resource": {
                "docId": request.resource.doc_id,
                "visibility": request.resource.visibility,
                "policyRef": request.resource.policy_ref,
            },
            "safeMode": request.safe_mode,
            "readOnly": request.read_only,
        }
        body = json.dumps(payload).encode("utf-8")

        headers = {
            "content-type": "application/json",
            "accept": "application/json",
            "x-acl-auth-mode": self._config.auth_mode,
        }
        if request.auth.trace_id:
            headers["x-trace-id"] = request.auth.trace_id
        if self._config.idp_issuer:
            headers["x-idp-issuer"] = self._config.idp_issuer
        if self._config.static_bearer_token:
            headers["authorization"] = f"Bearer {self._config.static_bearer_token}"

        outbound = urllib_request.Request(
            self._config.endpoint,
            data=body,
            headers=headers,
            method="POST",
        )

        try:
            with urllib_request.urlopen(outbound, timeout=self._config.timeout_seconds) as response:  # noqa: S310
                response_text = response.read().decode("utf-8")
        except urllib_error.HTTPError as exc:
            if exc.code in {400, 401, 403, 422}:
                raise AccessControlInvalidPolicyError("policy adapter rejected request") from exc
            raise AccessControlUnreachableError("policy adapter returned retryable error") from exc
        except urllib_error.URLError as exc:
            raise AccessControlUnreachableError("policy adapter unreachable") from exc
        except TimeoutError as exc:
            raise AccessControlUnreachableError("policy adapter timeout") from exc

        try:
            decoded = json.loads(response_text)
        except json.JSONDecodeError as exc:
            raise AccessControlInvalidPolicyError("policy adapter response is not json") from exc

        allow = decoded.get("allow")
        if not isinstance(allow, bool):
            raise AccessControlInvalidPolicyError("policy adapter response missing boolean allow")

        read_only = decoded.get("readOnly", False)
        if not isinstance(read_only, bool):
            raise AccessControlInvalidPolicyError("policy adapter readOnly must be boolean")

        reason = decoded.get("reason")
        if reason is not None and not isinstance(reason, str):
            raise AccessControlInvalidPolicyError("policy adapter reason must be string")

        return AccessDecision(allow=allow, read_only=read_only, reason=reason)


def _read_only_fallback(reason: FailSafeReason, *, action: AccessAction) -> AccessDecision:
    if action == "read":
        return AccessDecision(allow=True, read_only=True, reason=reason)
    return AccessDecision(allow=False, read_only=True, reason=reason)


def apply_local_failsafe(request: AccessRequest, mode: FailSafeMode) -> AccessDecision | None:
    """Local guardrails that do not interpret RBAC logic.

    Priority: safe_mode -> read_only -> policy_ref fail-safe.
    """

    if request.safe_mode and request.action in {"export", "share"}:
        return AccessDecision(allow=False, reason="safe_mode")

    if request.read_only and request.action in {"write", "export", "share"}:
        return AccessDecision(allow=False, read_only=True, reason="read_only")

    visibility = request.resource.visibility
    if visibility not in {"Org", "Restricted"}:
        return None

    if request.resource.policy_ref:
        return None

    if mode == "deny":
        return AccessDecision(allow=False, reason="policy_ref_missing")
    return _read_only_fallback("policy_ref_missing", action=request.action)


def apply_adapter_failsafe(
    *,
    request: AccessRequest,
    mode: FailSafeMode,
    reason: Literal["policy_ref_unreachable", "policy_ref_invalid", "adapter_error"],
) -> AccessDecision:
    if mode == "deny":
        return AccessDecision(allow=False, reason=reason)
    return _read_only_fallback(reason, action=request.action)


def resolve_access_decision(
    *,
    adapter: AccessControlAdapter,
    request: AccessRequest,
    fail_safe_mode: FailSafeMode,
) -> AccessDecision:
    local = apply_local_failsafe(request, fail_safe_mode)
    if local is not None:
        return local

    try:
        decision = adapter.authorize(request)
    except AccessControlUnreachableError:
        return apply_adapter_failsafe(request=request, mode=fail_safe_mode, reason="policy_ref_unreachable")
    except AccessControlInvalidPolicyError:
        return apply_adapter_failsafe(request=request, mode=fail_safe_mode, reason="policy_ref_invalid")
    except Exception:
        return apply_adapter_failsafe(request=request, mode=fail_safe_mode, reason="adapter_error")

    if not isinstance(decision, AccessDecision):
        return apply_adapter_failsafe(request=request, mode=fail_safe_mode, reason="adapter_error")

    return decision


def enforce_access(decision: AccessDecision, *, action: AccessAction) -> None:  # noqa: ARG001
    if decision.allow:
        return

    detail = "Access denied"
    if decision.reason:
        detail = f"Access denied: {decision.reason}"
    raise HTTPException(status_code=403, detail=detail)


def parse_csv_header(value: str | None) -> tuple[str, ...]:
    if value is None:
        return ()
    items = [item.strip() for item in value.split(",")]
    return tuple(item for item in items if item and item.lower() != "null")


def normalize_policy_ref(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    if not normalized or normalized.lower() == "null":
        return None
    return normalized


def parse_visibility(value: str | None) -> Visibility | None:
    if value is None:
        return None
    normalized = value.strip()
    if normalized in {"Public", "Unlisted", "Org", "Restricted"}:
        return cast(Visibility, normalized)
    return None


def build_access_control_adapter(*, adapter_name: str) -> AccessControlAdapter:
    if adapter_name == "noop":
        return NoopAccessControlAdapter()
    if adapter_name == "mock":
        return MockAccessControlAdapter()
    if adapter_name == "external_http":
        from kj_atlas_api.settings import settings

        endpoint = settings.access_control_external_http_endpoint
        if endpoint:
            return ExternalPolicyAccessControlAdapter(
                config=ExternalPolicyAdapterConfig(
                    endpoint=endpoint,
                    timeout_seconds=settings.access_control_external_http_timeout_seconds,
                    auth_mode=cast(AdapterAuthMode, settings.access_control_external_http_auth_mode),
                    static_bearer_token=settings.access_control_external_http_static_bearer_token,
                    idp_issuer=settings.access_control_external_http_idp_issuer,
                )
            )
    return NoopAccessControlAdapter()
