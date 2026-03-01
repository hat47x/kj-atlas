from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol

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
    roles: tuple[str, ...] = ()
    groups: tuple[str, ...] = ()
    trace_id: str | None = None


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
    if value in {"Public", "Unlisted", "Org", "Restricted"}:
        return value
    return None


def build_access_control_adapter(*, adapter_name: str) -> AccessControlAdapter:
    if adapter_name == "noop":
        return NoopAccessControlAdapter()
    if adapter_name == "mock":
        return MockAccessControlAdapter()
    return NoopAccessControlAdapter()
