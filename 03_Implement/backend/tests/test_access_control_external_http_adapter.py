from __future__ import annotations

import json
from urllib import error as urllib_error

import pytest

from kj_atlas_api.access_control import (
    AccessControlInvalidPolicyError,
    AccessControlUnreachableError,
    AccessRequest,
    AccessResource,
    AuthContext,
    ExternalPolicyAccessControlAdapter,
    ExternalPolicyAdapterConfig,
    build_access_control_adapter,
    resolve_access_decision,
)
from kj_atlas_api.settings import Settings
from kj_atlas_api.tenant_context import TenantContext


class _Response:
    def __init__(self, payload: dict):
        self._body = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):  # noqa: ANN001
        return False


def _request() -> AccessRequest:
    return AccessRequest(
        action="export",
        auth=AuthContext(actor_ref="user-1", roles=("editor",), groups=("org:a",), trace_id="trace-1"),
        resource=AccessResource(doc_id="doc-1", visibility="Org", policy_ref="opa://policy/v1"),
        safe_mode=False,
        read_only=False,
    )


def test_external_http_adapter_forwards_request_and_parses_decision(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def _urlopen(request, timeout_seconds):  # noqa: ANN001
        captured["url"] = request.full_url
        captured["timeout"] = timeout_seconds
        captured["auth"] = request.headers.get("Authorization")
        captured["auth_mode"] = request.headers.get("X-acl-auth-mode")
        captured["issuer"] = request.headers.get("X-idp-issuer")
        captured["trace"] = request.headers.get("X-trace-id")
        captured["body"] = json.loads(request.data.decode("utf-8"))
        return _Response({"allow": True, "readOnly": True, "reason": "external_read_only"})

    monkeypatch.setattr("kj_atlas_api.access_control.open_trusted_http", _urlopen)

    adapter = ExternalPolicyAccessControlAdapter(
        config=ExternalPolicyAdapterConfig(
            endpoint="https://policy.example.local/evaluate",
            timeout_seconds=0.75,
            auth_mode="oidc",
            static_bearer_token="token-abc",
            idp_issuer="https://issuer.example.local/",
        )
    )

    decision = adapter.authorize(_request())

    assert decision.allow is True
    assert decision.read_only is True
    assert decision.reason == "external_read_only"
    assert captured["url"] == "https://policy.example.local/evaluate"
    assert captured["timeout"] == 0.75
    assert captured["auth"] == "Bearer token-abc"
    assert captured["auth_mode"] == "oidc"
    assert captured["issuer"] == "https://issuer.example.local/"
    assert captured["trace"] == "trace-1"
    assert captured["body"] == {
        "action": "export",
        "auth": {
            "actorRef": "user-1",
            "roles": ["editor"],
            "groups": ["org:a"],
            "traceId": "trace-1",
        },
        "resource": {
            "docId": "doc-1",
            "visibility": "Org",
            "policyRef": "opa://policy/v1",
        },
        "safeMode": False,
        "readOnly": False,
    }


def test_external_http_adapter_forwards_server_resolved_tenant(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def _urlopen(request, timeout_seconds):  # noqa: ANN001, ARG001
        captured["body"] = json.loads(request.data.decode("utf-8"))
        return _Response({"allow": True})

    monkeypatch.setattr("kj_atlas_api.access_control.open_trusted_http", _urlopen)
    adapter = ExternalPolicyAccessControlAdapter(
        config=ExternalPolicyAdapterConfig(
            endpoint="https://policy.example.local/evaluate"
        )
    )
    tenant = TenantContext(
        tenant_id="tenant-a",
        membership_id="membership-a",
        resolved_by="verified_claim",
    )

    decision = adapter.authorize(
        AccessRequest(
            action="read",
            auth=AuthContext(actor_ref="user-1", user_id="user-1"),
            tenant=tenant,
            resource=AccessResource(doc_id="doc-1", tenant_id="tenant-a"),
        )
    )

    assert decision.allow is True
    assert captured["body"] == {
        "action": "read",
        "auth": {
            "actorRef": "user-1",
            "roles": [],
            "groups": [],
            "userId": "user-1",
        },
        "resource": {
            "docId": "doc-1",
            "visibility": None,
            "policyRef": None,
            "tenantId": "tenant-a",
            "kind": "document",
        },
        "tenant": {
            "tenantId": "tenant-a",
            "membershipId": "membership-a",
            "resolvedBy": "verified_claim",
        },
        "safeMode": False,
        "readOnly": False,
    }


def test_external_http_adapter_error_mapping(monkeypatch: pytest.MonkeyPatch) -> None:
    adapter = ExternalPolicyAccessControlAdapter(
        config=ExternalPolicyAdapterConfig(endpoint="https://policy.example.local/evaluate")
    )

    def _raise_unreachable(request, timeout_seconds):  # noqa: ANN001
        raise urllib_error.URLError("down")

    monkeypatch.setattr("kj_atlas_api.access_control.open_trusted_http", _raise_unreachable)

    with pytest.raises(AccessControlUnreachableError):
        adapter.authorize(_request())

    def _raise_invalid(request, timeout_seconds):  # noqa: ANN001
        raise urllib_error.HTTPError(
            url=request.full_url,
            code=403,
            msg="forbidden",
            hdrs=None,
            fp=None,
        )

    monkeypatch.setattr("kj_atlas_api.access_control.open_trusted_http", _raise_invalid)

    with pytest.raises(AccessControlInvalidPolicyError):
        adapter.authorize(_request())


def test_build_access_control_adapter_external_http_fallbacks_to_noop_when_endpoint_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("kj_atlas_api.settings.settings.access_control_external_http_endpoint", None)

    adapter = build_access_control_adapter(adapter_name="external_http")

    assert adapter.name == "noop"


def test_external_http_auth_mode_setting_rejects_invalid_value() -> None:
    with pytest.raises(ValueError):
        Settings(ACCESS_CONTROL_EXTERNAL_HTTP_AUTH_MODE="kerberos")


def test_external_http_adapter_unreachable_uses_existing_fail_safe_reason(monkeypatch: pytest.MonkeyPatch) -> None:
    def _raise_unreachable(request, timeout_seconds):  # noqa: ANN001
        raise urllib_error.URLError("down")

    monkeypatch.setattr("kj_atlas_api.access_control.open_trusted_http", _raise_unreachable)

    adapter = ExternalPolicyAccessControlAdapter(
        config=ExternalPolicyAdapterConfig(endpoint="https://policy.example.local/evaluate")
    )

    decision = resolve_access_decision(adapter=adapter, request=_request(), fail_safe_mode="deny")

    assert decision.allow is False
    assert decision.reason == "policy_ref_unreachable"
