from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Literal, Protocol
from urllib import error, request

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


class MockAccessControlAdapter:
    name = "mock"

    def __init__(self, *, allow: bool, reason: str | None = None):
        self._allow = allow
        self._reason = reason

    def authorize(self, request: AccessRequest) -> AccessDecision:  # noqa: ARG002
        return AccessDecision(allow=self._allow, reason=self._reason)


class HttpAccessControlAdapter:
    name = "http"

    def __init__(self, *, endpoint: str, api_key: str | None = None, timeout_seconds: float = 2.0):
        self._endpoint = endpoint
        self._api_key = api_key
        self._timeout_seconds = timeout_seconds

    def authorize(self, request_payload: AccessRequest) -> AccessDecision:
        payload = {
            "action": request_payload.action,
            "safeMode": request_payload.safe_mode,
            "readOnly": request_payload.read_only,
            "subject": {
                "actorRef": request_payload.subject.actor_ref,
                "roles": list(request_payload.subject.roles),
                "groups": list(request_payload.subject.groups),
            },
            "resource": {
                "docId": request_payload.resource.doc_id,
                "visibility": request_payload.resource.visibility,
                "policyRef": request_payload.resource.policy_ref,
            },
        }
        body = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        req_obj = request.Request(self._endpoint, data=body, headers=headers, method="POST")
        try:
            with request.urlopen(req_obj, timeout=self._timeout_seconds) as response:
                raw = response.read().decode("utf-8")
        except error.HTTPError as exc:
            raise RuntimeError(f"policy_ref_invalid:{exc.code}") from exc
        except error.URLError as exc:
            raise RuntimeError(f"policy_ref_unreachable:{exc.reason}") from exc

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError("policy_ref_invalid:invalid_json") from exc

        if not isinstance(parsed, dict) or not isinstance(parsed.get("allow"), bool):
            raise RuntimeError("policy_ref_invalid:decision_schema")

        read_only = parsed.get("readOnly")
        if read_only is not None and not isinstance(read_only, bool):
            raise RuntimeError("policy_ref_invalid:decision_schema")

        reason = parsed.get("reason")
        if reason is not None and not isinstance(reason, str):
            raise RuntimeError("policy_ref_invalid:decision_schema")

        return AccessDecision(allow=parsed["allow"], read_only=bool(read_only), reason=reason)


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
    return tuple(item for item in items if item and item.lower() != "null")


def normalize_policy_ref(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    if normalized == "" or normalized.lower() == "null":
        return None
    return normalized


def apply_adapter_error_failsafe(
    request: AccessRequest,
    *,
    mode: FailSafeMode,
    reason_code: str,
) -> AccessDecision | None:
    if request.resource.visibility not in {"Org", "Restricted"}:
        return None
    if mode == "deny":
        return AccessDecision(allow=False, reason=reason_code)
    if request.action == "read":
        return AccessDecision(allow=True, read_only=True, reason=reason_code)
    return AccessDecision(allow=False, reason=reason_code)


def build_access_control_adapter(
    *,
    adapter_name: str,
    http_endpoint: str | None = None,
    http_api_key: str | None = None,
    http_timeout_seconds: float = 2.0,
    mock_allow: bool = True,
    mock_reason: str | None = None,
) -> AccessControlAdapter:
    if adapter_name == "noop":
        return NoopAccessControlAdapter()
    if adapter_name == "mock":
        return MockAccessControlAdapter(allow=mock_allow, reason=mock_reason)
    if adapter_name == "http" and http_endpoint:
        return HttpAccessControlAdapter(
            endpoint=http_endpoint,
            api_key=http_api_key,
            timeout_seconds=http_timeout_seconds,
        )
    return NoopAccessControlAdapter()
