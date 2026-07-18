from __future__ import annotations

import json
from urllib import error as urllib_error

import pytest

from kj_atlas_api.session_context import KNOWN_EFFECTIVE_CAPABILITIES
from kj_atlas_api.settings import Settings
from kj_atlas_api.tenant_capability import (
    MAX_CAPABILITY_RESPONSE_BYTES,
    ExternalHttpTenantCapabilityResolver,
    ExternalTenantCapabilityConfig,
    TenantCapabilityInvalidResponseError,
    TenantCapabilityUnavailableError,
    UnavailableTenantCapabilityResolver,
    build_tenant_capability_resolver,
)
from kj_atlas_api.tenant_context import TenantContext


class _Response:
    def __init__(self, body: bytes) -> None:
        self._body = body
        self.read_limit: int | None = None

    def read(self, limit: int) -> bytes:
        self.read_limit = limit
        return self._body

    def __enter__(self) -> _Response:
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:  # noqa: ANN001
        return False


def _tenant(
    *,
    tenant_id: str = "tenant-a",
    membership_id: str | None = "membership-a",
) -> TenantContext:
    return TenantContext(
        tenant_id=tenant_id,
        membership_id=membership_id,
        resolved_by="verified_claim",
    )


def _resolver(*, api_key: str | None = "capability-api-key") -> ExternalHttpTenantCapabilityResolver:
    return ExternalHttpTenantCapabilityResolver(
        config=ExternalTenantCapabilityConfig(
            endpoint="https://capability.example.invalid/v1/resolve",
            timeout_seconds=0.8,
            api_key=api_key,
        )
    )


def test_external_capability_resolver_sends_server_context_and_parses_snapshot(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}
    response = _Response(
        json.dumps(
            {
                "effectiveCapabilities": [
                    "document.read",
                    "document.policy.manage",
                ],
                "capabilityVersion": "capability-v7",
            }
        ).encode()
    )

    def _urlopen(request, timeout_seconds):  # noqa: ANN001
        captured["url"] = request.full_url
        captured["method"] = request.method
        captured["authorization"] = request.headers.get("Authorization")
        captured["timeout"] = timeout_seconds
        captured["body"] = json.loads(request.data.decode())
        return response

    monkeypatch.setattr(
        "kj_atlas_api.tenant_capability.open_trusted_http",
        _urlopen,
    )

    snapshot = _resolver().resolve(
        db=None,  # type: ignore[arg-type]
        principal_id="principal-1",
        tenant=_tenant(),
    )

    assert snapshot.effective_capabilities == (
        "document.read",
        "document.policy.manage",
    )
    assert snapshot.capability_version == "capability-v7"
    assert captured == {
        "url": "https://capability.example.invalid/v1/resolve",
        "method": "POST",
        "authorization": "Bearer capability-api-key",
        "timeout": 0.8,
        "body": {
            "principalId": "principal-1",
            "tenantId": "tenant-a",
            "membershipId": "membership-a",
        },
    }
    assert response.read_limit == MAX_CAPABILITY_RESPONSE_BYTES + 1


@pytest.mark.parametrize(
    "body",
    [
        b"not-json",
        json.dumps({}).encode(),
        json.dumps(
            {
                "effectiveCapabilities": [],
                "capabilityVersion": "v1",
                "roles": ["admin"],
            }
        ).encode(),
        json.dumps(
            {"effectiveCapabilities": "document.read", "capabilityVersion": "v1"}
        ).encode(),
        json.dumps(
            {"effectiveCapabilities": ["unknown.capability"], "capabilityVersion": "v1"}
        ).encode(),
        json.dumps(
            {
                "effectiveCapabilities": ["document.read", "document.read"],
                "capabilityVersion": "v1",
            }
        ).encode(),
        json.dumps(
            {"effectiveCapabilities": ["document.read"], "capabilityVersion": " bad "}
        ).encode(),
        b"{" + b"x" * MAX_CAPABILITY_RESPONSE_BYTES + b"}",
    ],
    ids=[
        "not-json",
        "missing-fields",
        "extra-roles",
        "capabilities-not-list",
        "unknown-capability",
        "duplicate-capability",
        "invalid-version",
        "response-too-large",
    ],
)
def test_external_capability_resolver_rejects_invalid_snapshot_without_reflection(
    monkeypatch: pytest.MonkeyPatch,
    body: bytes,
) -> None:
    monkeypatch.setattr(
        "kj_atlas_api.tenant_capability.open_trusted_http",
        lambda request, timeout_seconds: _Response(body),  # noqa: ARG005
    )

    with pytest.raises(TenantCapabilityInvalidResponseError) as exc_info:
        _resolver(api_key=None).resolve(
            db=None,  # type: ignore[arg-type]
            principal_id="principal-1",
            tenant=_tenant(),
        )

    error_text = str(exc_info.value)
    assert "admin" not in error_text
    assert "unknown.capability" not in error_text


@pytest.mark.parametrize(
    "failure",
    [
        urllib_error.URLError("internal service location"),
        TimeoutError("internal timeout detail"),
        OSError("internal socket detail"),
    ],
)
def test_external_capability_resolver_normalizes_transport_failure(
    monkeypatch: pytest.MonkeyPatch,
    failure: Exception,
) -> None:
    def _raise(request, timeout_seconds):  # noqa: ANN001, ARG001
        raise failure

    monkeypatch.setattr(
        "kj_atlas_api.tenant_capability.open_trusted_http",
        _raise,
    )

    with pytest.raises(TenantCapabilityUnavailableError) as exc_info:
        _resolver().resolve(
            db=None,  # type: ignore[arg-type]
            principal_id="principal-1",
            tenant=_tenant(),
        )

    assert str(exc_info.value) == "capability service is unavailable"


def test_external_capability_resolver_rejects_missing_membership_before_transport(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transport_called = False

    def _urlopen(request, timeout_seconds):  # noqa: ANN001, ARG001
        nonlocal transport_called
        transport_called = True
        return _Response(b"{}")

    monkeypatch.setattr(
        "kj_atlas_api.tenant_capability.open_trusted_http",
        _urlopen,
    )

    with pytest.raises(TenantCapabilityUnavailableError):
        _resolver().resolve(
            db=None,  # type: ignore[arg-type]
            principal_id="principal-1",
            tenant=_tenant(membership_id=None),
        )

    assert transport_called is False


@pytest.mark.parametrize(
    ("principal_id", "tenant"),
    [
        (" principal-1", _tenant()),
        ("principal\u200b1", _tenant()),
        ("principal-1", _tenant(tenant_id="x" * 257)),
        ("principal-1", _tenant(membership_id="membership\n1")),
    ],
    ids=[
        "principal-whitespace",
        "principal-non-printable",
        "tenant-too-long",
        "membership-control-character",
    ],
)
def test_external_capability_resolver_rejects_invalid_context_before_transport(
    monkeypatch: pytest.MonkeyPatch,
    principal_id: str,
    tenant: TenantContext,
) -> None:
    transport_called = False

    def _unexpected_transport(request, timeout_seconds):  # noqa: ANN001, ARG001
        nonlocal transport_called
        transport_called = True
        raise AssertionError("transport must not be called")

    monkeypatch.setattr(
        "kj_atlas_api.tenant_capability.open_trusted_http",
        _unexpected_transport,
    )

    with pytest.raises(TenantCapabilityUnavailableError) as exc_info:
        _resolver().resolve(
            db=None,  # type: ignore[arg-type]
            principal_id=principal_id,
            tenant=tenant,
        )

    assert str(exc_info.value) == "tenant capability context is unavailable"
    assert transport_called is False


def test_external_capability_resolver_rejects_oversized_request_before_transport(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "kj_atlas_api.tenant_capability.MAX_CAPABILITY_REQUEST_BYTES",
        32,
    )
    monkeypatch.setattr(
        "kj_atlas_api.tenant_capability.open_trusted_http",
        lambda request, timeout_seconds: (_ for _ in ()).throw(  # noqa: ARG005
            AssertionError("transport must not be called")
        ),
    )

    with pytest.raises(TenantCapabilityUnavailableError):
        _resolver().resolve(
            db=None,  # type: ignore[arg-type]
            principal_id="principal-1",
            tenant=_tenant(),
        )


def test_external_capability_resolver_maps_http_rejection_without_detail(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _raise(request, timeout_seconds):  # noqa: ANN001, ARG001
        raise urllib_error.HTTPError(
            url="https://capability.example.invalid/v1/resolve",
            code=403,
            msg="secret internal policy detail",
            hdrs=None,
            fp=None,
        )

    monkeypatch.setattr(
        "kj_atlas_api.tenant_capability.open_trusted_http",
        _raise,
    )

    with pytest.raises(TenantCapabilityInvalidResponseError) as exc_info:
        _resolver().resolve(
            db=None,  # type: ignore[arg-type]
            principal_id="principal-1",
            tenant=_tenant(),
        )

    assert str(exc_info.value) == "capability service rejected the lookup"


def test_capability_builder_defaults_unavailable_and_builds_only_when_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "kj_atlas_api.tenant_capability.settings.tenant_capability_resolver",
        "none",
    )
    assert isinstance(
        build_tenant_capability_resolver(),
        UnavailableTenantCapabilityResolver,
    )

    monkeypatch.setattr(
        "kj_atlas_api.tenant_capability.settings.tenant_capability_resolver",
        "external_http",
    )
    monkeypatch.setattr(
        "kj_atlas_api.tenant_capability.settings.tenant_capability_http_endpoint",
        "https://capability.example.invalid/v1/resolve",
    )
    monkeypatch.setattr(
        "kj_atlas_api.tenant_capability.settings.tenant_capability_http_api_key",
        "api-key",
    )
    monkeypatch.setattr(
        "kj_atlas_api.tenant_capability.settings.tenant_capability_http_timeout_seconds",
        0.5,
    )
    assert isinstance(
        build_tenant_capability_resolver(),
        ExternalHttpTenantCapabilityResolver,
    )


@pytest.mark.parametrize(
    "overrides",
    [
        {"KJ_ATLAS_TENANT_CAPABILITY_RESOLVER": "unknown"},
        {"KJ_ATLAS_TENANT_CAPABILITY_RESOLVER": "external_http"},
        {
            "KJ_ATLAS_TENANT_CAPABILITY_RESOLVER": "none",
            "KJ_ATLAS_TENANT_CAPABILITY_HTTP_ENDPOINT": (
                "https://capability.example.invalid/resolve"
            ),
        },
        {
            "KJ_ATLAS_TENANT_CAPABILITY_RESOLVER": "external_http",
            "KJ_ATLAS_TENANT_CAPABILITY_HTTP_ENDPOINT": (
                "http://capability.example.invalid/resolve"
            ),
        },
        {
            "KJ_ATLAS_TENANT_CAPABILITY_RESOLVER": "external_http",
            "KJ_ATLAS_TENANT_CAPABILITY_HTTP_ENDPOINT": (
                "https://user:pass@capability.example.invalid/resolve"
            ),
        },
        {
            "KJ_ATLAS_TENANT_CAPABILITY_RESOLVER": "external_http",
            "KJ_ATLAS_TENANT_CAPABILITY_HTTP_ENDPOINT": (
                "https://capability.example.invalid/resolve?token=secret"
            ),
        },
        {
            "KJ_ATLAS_TENANT_CAPABILITY_RESOLVER": "external_http",
            "KJ_ATLAS_TENANT_CAPABILITY_HTTP_ENDPOINT": (
                "https://capability.example.invalid/resolve"
            ),
            "KJ_ATLAS_TENANT_CAPABILITY_HTTP_API_KEY": "invalid key",
        },
        {"KJ_ATLAS_TENANT_CAPABILITY_HTTP_TIMEOUT_SECONDS": 31},
    ],
)
def test_capability_settings_reject_unsafe_configuration(
    overrides: dict[str, object],
) -> None:
    with pytest.raises(ValueError):
        Settings(**overrides)


def test_capability_settings_allow_https_and_hide_secret_input() -> None:
    configured = Settings(
        KJ_ATLAS_TENANT_CAPABILITY_RESOLVER="external_http",
        KJ_ATLAS_TENANT_CAPABILITY_HTTP_ENDPOINT=(
            "https://capability.example.invalid/resolve"
        ),
        KJ_ATLAS_TENANT_CAPABILITY_HTTP_API_KEY="api-key",
    )
    assert configured.tenant_capability_resolver == "external_http"

    raw_secret = "super secret capability key"
    endpoint_with_secret = "https://capability.example.invalid/resolve?token=raw-secret"
    with pytest.raises(ValueError) as exc_info:
        Settings(
            KJ_ATLAS_TENANT_CAPABILITY_RESOLVER="external_http",
            KJ_ATLAS_TENANT_CAPABILITY_HTTP_ENDPOINT=endpoint_with_secret,
            KJ_ATLAS_TENANT_CAPABILITY_HTTP_API_KEY=raw_secret,
        )
    error_text = str(exc_info.value)
    assert raw_secret not in error_text
    assert endpoint_with_secret not in error_text


def test_known_capability_contract_contains_independent_admin_capability() -> None:
    assert "document.policy.manage" in KNOWN_EFFECTIVE_CAPABILITIES
    assert "document.policy.manage" != "document.write"
