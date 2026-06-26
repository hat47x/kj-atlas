from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Literal, Protocol, cast
from urllib import error as urllib_error
from urllib import request as urllib_request

from fastapi import HTTPException

from kj_atlas_api.settings import settings

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
    auth: AuthContext | None = None
    resource: AccessResource | None = None
    safe_mode: bool = False
    read_only: bool = False
    subject: AccessSubject | None = None


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

    def __init__(self, *, mock_allow: bool = True, mock_reason: str = "mock") -> None:
        self._mock_allow = mock_allow
        self._mock_reason = mock_reason

    def authorize(self, request: AccessRequest) -> AccessDecision:
        if not self._mock_allow:
            return AccessDecision(allow=False, reason=self._mock_reason)
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
        auth_source = request.auth
        if auth_source is None and request.subject is not None:
            auth_source = AuthContext(
                actor_ref=request.subject.actor_ref,
                roles=request.subject.roles,
                groups=request.subject.groups,
            )

        auth_payload: dict[str, object] = {
            "actorRef": auth_source.actor_ref,
            "roles": list(auth_source.roles),
            "groups": list(auth_source.groups),
            "traceId": getattr(auth_source, "trace_id", None),
        }
        if auth_source.user_id is not None:
            auth_payload["userId"] = auth_source.user_id
        if auth_source.provider is not None:
            auth_payload["provider"] = auth_source.provider
        if auth_source.external_uid is not None:
            auth_payload["externalUid"] = auth_source.external_uid
        if auth_source.amr is not None:
            auth_payload["amr"] = auth_source.amr
        if auth_source.acr is not None:
            auth_payload["acr"] = auth_source.acr
        if auth_source.aal is not None:
            auth_payload["aal"] = auth_source.aal
        if auth_source.auth_time is not None:
            auth_payload["authTime"] = auth_source.auth_time

        resource_source = request.resource
        if resource_source is None:
            resource_source = AccessResource(doc_id="")

        payload = {
            "action": request.action,
            "auth": auth_payload,
            "resource": {
                "docId": resource_source.doc_id,
                "visibility": resource_source.visibility,
                "policyRef": resource_source.policy_ref,
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
        if auth_source.trace_id:
            headers["x-trace-id"] = auth_source.trace_id
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


def build_access_control_adapter(*, adapter_name: str, mock_allow: bool | None = None, mock_reason: str | None = None, http_endpoint: str | None = None, http_api_key: str | None = None, http_timeout_seconds: float | None = None) -> AccessControlAdapter:
    if adapter_name == "noop":
        return NoopAccessControlAdapter()
    if adapter_name in ("mock", "http", "external_http", "external"):
        pass  # handled below
    else:
        return NoopAccessControlAdapter()

    if adapter_name == "mock":
        return MockAccessControlAdapter(
            mock_allow=mock_allow if mock_allow is not None else True,
            mock_reason=mock_reason if mock_reason is not None else "mock",
        )

    endpoint = http_endpoint or _get_configured_endpoint()
    if endpoint:
        return ExternalPolicyAccessControlAdapter(
            config=ExternalPolicyAdapterConfig(
                endpoint=endpoint,
                timeout_seconds=http_timeout_seconds or settings.access_control_external_http_timeout_seconds,
                auth_mode=cast(AdapterAuthMode, settings.access_control_external_http_auth_mode),
                static_bearer_token=http_api_key or settings.access_control_external_http_static_bearer_token,
                idp_issuer=settings.access_control_external_http_idp_issuer,
            )
        )
    return NoopAccessControlAdapter()


def _get_configured_endpoint() -> str | None:
    return settings.access_control_external_http_endpoint
