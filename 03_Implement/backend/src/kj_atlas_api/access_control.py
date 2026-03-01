from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol

from fastapi import HTTPException

AccessAction = Literal["read", "write", "export", "share"]
Visibility = Literal["Public", "Unlisted", "Org", "Restricted"]
FailSafeMode = Literal["deny", "read_only"]


@dataclass(frozen=True)
class AccessSubject:
    actor_ref: str | None
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
    subject: AccessSubject
    resource: AccessResource
    safe_mode: bool
    read_only: bool


@dataclass(frozen=True)
class AccessDecision:
    allow: bool
    read_only: bool = False
    reason: str | None = None


class AccessControlAdapter(Protocol):
    """Externalized authorization adapter contract.

    The adapter can call external RBAC/ABAC engines. Application core must not
    embed role/group/policy evaluation logic.
    """

    name: str

    def authorize(self, request: AccessRequest) -> AccessDecision:
        ...


class NoopAccessControlAdapter:
    name = "noop"

    def authorize(self, request: AccessRequest) -> AccessDecision:  # noqa: ARG002
        return AccessDecision(allow=True)


def apply_local_failsafe(request: AccessRequest, mode: FailSafeMode) -> AccessDecision | None:
    """Minimal local guard when visibility requires policyRef but it is missing."""

    visibility = request.resource.visibility
    if visibility not in {"Org", "Restricted"}:
        return None
    if request.resource.policy_ref:
        return None

    if mode == "deny":
        return AccessDecision(allow=False, reason="policy_ref_missing")

    if request.action == "read":
        return AccessDecision(allow=True, read_only=True, reason="policy_ref_missing_read_only")
    return AccessDecision(allow=False, reason="policy_ref_missing_read_only")


def enforce_access(decision: AccessDecision, *, action: AccessAction) -> None:
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
    return tuple(item for item in items if item)


def build_access_control_adapter(*, adapter_name: str) -> AccessControlAdapter:
    if adapter_name == "noop":
        return NoopAccessControlAdapter()
    return NoopAccessControlAdapter()
