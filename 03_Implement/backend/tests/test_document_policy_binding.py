from __future__ import annotations

import json
from urllib import error as urllib_error

import pytest

from kj_atlas_api.document_access_resource import UnavailableDocumentPolicyBindingResolver
from kj_atlas_api.document_policy_binding import (
    MAX_BINDING_RESPONSE_BYTES,
    DocumentPolicyBindingInvalidResponseError,
    DocumentPolicyBindingUnavailableError,
    ExternalDocumentPolicyBindingConfig,
    ExternalHttpDocumentPolicyBindingResolver,
    build_document_policy_binding_resolver,
)
from kj_atlas_api.settings import Settings
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


def _tenant(*, tenant_id: str = "tenant-a") -> TenantContext:
    return TenantContext(
        tenant_id=tenant_id,
        membership_id="membership-a",
        resolved_by="verified_claim",
    )


def _resolver(*, api_key: str | None = "binding-api-key") -> ExternalHttpDocumentPolicyBindingResolver:
    return ExternalHttpDocumentPolicyBindingResolver(
        config=ExternalDocumentPolicyBindingConfig(
            endpoint="https://binding.example.invalid/v1/resolve",
            timeout_seconds=0.75,
            api_key=api_key,
        )
    )


def test_external_resolver_sends_only_opaque_lookup_and_returns_transient_policy_ref(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}
    response = _Response(json.dumps({"policyRef": "opa://runtime/policy-1"}).encode())

    def _urlopen(request, timeout_seconds):  # noqa: ANN001
        captured["url"] = request.full_url
        captured["method"] = request.method
        captured["authorization"] = request.headers.get("Authorization")
        captured["content_type"] = request.headers.get("Content-type")
        captured["timeout"] = timeout_seconds
        captured["body"] = json.loads(request.data.decode())
        return response

    monkeypatch.setattr(
        "kj_atlas_api.document_policy_binding.open_trusted_http",
        _urlopen,
    )

    policy_ref = _resolver().resolve(
        tenant=_tenant(),
        binding_id="binding-1",
        policy_version="policy-v3",
    )

    assert policy_ref == "opa://runtime/policy-1"
    assert captured == {
        "url": "https://binding.example.invalid/v1/resolve",
        "method": "POST",
        "authorization": "Bearer binding-api-key",
        "content_type": "application/json",
        "timeout": 0.75,
        "body": {
            "tenantId": "tenant-a",
            "bindingId": "binding-1",
            "policyVersion": "policy-v3",
        },
    }
    assert response.read_limit == MAX_BINDING_RESPONSE_BYTES + 1


@pytest.mark.parametrize(
    ("tenant_id", "binding_id", "policy_version"),
    [
        (" tenant-a", "binding-1", "policy-v1"),
        ("tenant-a", "binding\n1", "policy-v1"),
        ("tenant-a", "binding-1", "x" * 129),
        ("tenant\u200ba", "binding-1", "policy-v1"),
    ],
    ids=[
        "tenant-whitespace",
        "binding-control-character",
        "policy-version-too-long",
        "tenant-non-printable",
    ],
)
def test_external_resolver_rejects_invalid_lookup_before_transport(
    monkeypatch: pytest.MonkeyPatch,
    tenant_id: str,
    binding_id: str,
    policy_version: str,
) -> None:
    transport_called = False

    def _unexpected_transport(request, timeout_seconds):  # noqa: ANN001, ARG001
        nonlocal transport_called
        transport_called = True
        raise AssertionError("transport must not be called")

    monkeypatch.setattr(
        "kj_atlas_api.document_policy_binding.open_trusted_http",
        _unexpected_transport,
    )

    with pytest.raises(DocumentPolicyBindingUnavailableError) as exc_info:
        _resolver().resolve(
            tenant=_tenant(tenant_id=tenant_id),
            binding_id=binding_id,
            policy_version=policy_version,
        )

    assert str(exc_info.value) == "binding service lookup context is unavailable"
    assert transport_called is False


def test_external_resolver_rejects_oversized_lookup_before_transport(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "kj_atlas_api.document_policy_binding.MAX_BINDING_REQUEST_BYTES",
        32,
    )
    monkeypatch.setattr(
        "kj_atlas_api.document_policy_binding.open_trusted_http",
        lambda request, timeout_seconds: (_ for _ in ()).throw(  # noqa: ARG005
            AssertionError("transport must not be called")
        ),
    )

    with pytest.raises(DocumentPolicyBindingUnavailableError):
        _resolver().resolve(
            tenant=_tenant(),
            binding_id="binding-1",
            policy_version="policy-v1",
        )


@pytest.mark.parametrize(
    "body",
    [
        b"not-json",
        json.dumps({}).encode(),
        json.dumps({"policyRef": "ref", "token": "must-not-be-accepted"}).encode(),
        json.dumps({"policyRef": None}).encode(),
        json.dumps({"policyRef": " raw-secret "}).encode(),
        json.dumps({"policyRef": "raw-secret\n"}).encode(),
        json.dumps({"policyRef": "x" * 2049}).encode(),
        b"{" + b"x" * MAX_BINDING_RESPONSE_BYTES + b"}",
    ],
    ids=[
        "not-json",
        "missing-policy-ref",
        "extra-field",
        "null-policy-ref",
        "whitespace-policy-ref",
        "control-character",
        "policy-ref-too-long",
        "response-too-large",
    ],
)
def test_external_resolver_rejects_invalid_response_without_reflecting_value(
    monkeypatch: pytest.MonkeyPatch,
    body: bytes,
) -> None:
    monkeypatch.setattr(
        "kj_atlas_api.document_policy_binding.open_trusted_http",
        lambda request, timeout_seconds: _Response(body),  # noqa: ARG005
    )

    with pytest.raises(DocumentPolicyBindingInvalidResponseError) as exc_info:
        _resolver(api_key=None).resolve(
            tenant=_tenant(),
            binding_id="binding-1",
            policy_version="policy-v1",
        )

    assert "raw-secret" not in str(exc_info.value)
    assert "must-not-be-accepted" not in str(exc_info.value)


@pytest.mark.parametrize(
    "failure",
    [
        urllib_error.URLError("internal service location"),
        TimeoutError("internal timeout detail"),
        OSError("internal socket detail"),
    ],
)
def test_external_resolver_normalizes_transport_failure_without_leaking_details(
    monkeypatch: pytest.MonkeyPatch,
    failure: Exception,
) -> None:
    def _raise(request, timeout_seconds):  # noqa: ANN001, ARG001
        raise failure

    monkeypatch.setattr(
        "kj_atlas_api.document_policy_binding.open_trusted_http",
        _raise,
    )

    with pytest.raises(DocumentPolicyBindingUnavailableError) as exc_info:
        _resolver().resolve(
            tenant=_tenant(),
            binding_id="binding-1",
            policy_version="policy-v1",
        )

    assert str(exc_info.value) == "binding service is unavailable"


def test_external_resolver_maps_rejected_lookup_to_invalid_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _raise(request, timeout_seconds):  # noqa: ANN001, ARG001
        raise urllib_error.HTTPError(
            url="https://binding.example.invalid/v1/resolve",
            code=403,
            msg="secret internal denial",
            hdrs=None,
            fp=None,
        )

    monkeypatch.setattr(
        "kj_atlas_api.document_policy_binding.open_trusted_http",
        _raise,
    )

    with pytest.raises(DocumentPolicyBindingInvalidResponseError) as exc_info:
        _resolver().resolve(
            tenant=_tenant(),
            binding_id="binding-1",
            policy_version="policy-v1",
        )

    assert str(exc_info.value) == "binding service rejected the lookup"


def test_binding_resolver_builder_defaults_unavailable_and_builds_only_when_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "kj_atlas_api.document_policy_binding.settings.document_policy_binding_resolver",
        "none",
    )
    assert isinstance(
        build_document_policy_binding_resolver(),
        UnavailableDocumentPolicyBindingResolver,
    )

    monkeypatch.setattr(
        "kj_atlas_api.document_policy_binding.settings.document_policy_binding_resolver",
        "external_http",
    )
    monkeypatch.setattr(
        "kj_atlas_api.document_policy_binding.settings.document_policy_binding_http_endpoint",
        "https://binding.example.invalid/v1/resolve",
    )
    monkeypatch.setattr(
        "kj_atlas_api.document_policy_binding.settings.document_policy_binding_http_api_key",
        "api-key",
    )
    monkeypatch.setattr(
        "kj_atlas_api.document_policy_binding.settings.document_policy_binding_http_timeout_seconds",
        0.5,
    )
    assert isinstance(
        build_document_policy_binding_resolver(),
        ExternalHttpDocumentPolicyBindingResolver,
    )


@pytest.mark.parametrize(
    "overrides",
    [
        {"KJ_ATLAS_DOCUMENT_POLICY_BINDING_RESOLVER": "unknown"},
        {"KJ_ATLAS_DOCUMENT_POLICY_BINDING_RESOLVER": "external_http"},
        {
            "KJ_ATLAS_DOCUMENT_POLICY_BINDING_RESOLVER": "none",
            "KJ_ATLAS_DOCUMENT_POLICY_BINDING_HTTP_ENDPOINT": (
                "https://binding.example.invalid/resolve"
            ),
        },
        {
            "KJ_ATLAS_DOCUMENT_POLICY_BINDING_RESOLVER": "external_http",
            "KJ_ATLAS_DOCUMENT_POLICY_BINDING_HTTP_ENDPOINT": (
                "http://binding.example.invalid/resolve"
            ),
        },
        {
            "KJ_ATLAS_DOCUMENT_POLICY_BINDING_RESOLVER": "external_http",
            "KJ_ATLAS_DOCUMENT_POLICY_BINDING_HTTP_ENDPOINT": (
                "https://user:pass@binding.example.invalid/resolve"
            ),
        },
        {
            "KJ_ATLAS_DOCUMENT_POLICY_BINDING_RESOLVER": "external_http",
            "KJ_ATLAS_DOCUMENT_POLICY_BINDING_HTTP_ENDPOINT": (
                "https://binding.example.invalid/resolve?token=secret"
            ),
        },
        {
            "KJ_ATLAS_DOCUMENT_POLICY_BINDING_RESOLVER": "external_http",
            "KJ_ATLAS_DOCUMENT_POLICY_BINDING_HTTP_ENDPOINT": (
                "https://binding.example.invalid/resolve"
            ),
            "KJ_ATLAS_DOCUMENT_POLICY_BINDING_HTTP_API_KEY": "invalid key",
        },
        {"KJ_ATLAS_DOCUMENT_POLICY_BINDING_HTTP_TIMEOUT_SECONDS": 0},
    ],
)
def test_binding_resolver_settings_reject_unsafe_configuration(
    overrides: dict[str, object],
) -> None:
    with pytest.raises(ValueError):
        Settings(**overrides)


def test_binding_resolver_settings_allow_https_and_loopback_http() -> None:
    https = Settings(
        KJ_ATLAS_DOCUMENT_POLICY_BINDING_RESOLVER="external_http",
        KJ_ATLAS_DOCUMENT_POLICY_BINDING_HTTP_ENDPOINT=(
            "https://binding.example.invalid/resolve"
        ),
        KJ_ATLAS_DOCUMENT_POLICY_BINDING_HTTP_API_KEY="api-key",
    )
    loopback = Settings(
        KJ_ATLAS_DOCUMENT_POLICY_BINDING_RESOLVER="external_http",
        KJ_ATLAS_DOCUMENT_POLICY_BINDING_HTTP_ENDPOINT="http://127.0.0.1:9000/resolve",
    )

    assert https.document_policy_binding_resolver == "external_http"
    assert loopback.document_policy_binding_http_endpoint == "http://127.0.0.1:9000/resolve"


def test_binding_resolver_settings_error_does_not_reflect_secret_input() -> None:
    raw_secret = "super secret bearer value"
    endpoint_with_secret = "https://binding.example.invalid/resolve?token=raw-secret"

    with pytest.raises(ValueError) as exc_info:
        Settings(
            KJ_ATLAS_DOCUMENT_POLICY_BINDING_RESOLVER="external_http",
            KJ_ATLAS_DOCUMENT_POLICY_BINDING_HTTP_ENDPOINT=endpoint_with_secret,
            KJ_ATLAS_DOCUMENT_POLICY_BINDING_HTTP_API_KEY=raw_secret,
        )

    error_text = str(exc_info.value)
    assert raw_secret not in error_text
    assert endpoint_with_secret not in error_text
