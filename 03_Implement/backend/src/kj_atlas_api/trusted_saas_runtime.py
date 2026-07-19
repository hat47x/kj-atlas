from __future__ import annotations

from dataclasses import dataclass

from fastapi import FastAPI

from kj_atlas_api.active_tenant_session import ActiveTenantSessionPersister
from kj_atlas_api.auth_context import SaasIdentityContextResolver
from kj_atlas_api.document_access_resource import (
    ServerOwnedDocumentResourceResolver,
    SingleTenantHeaderResourceResolver,
)
from kj_atlas_api.document_policy_binding import build_document_policy_binding_resolver
from kj_atlas_api.runtime_bootstrap import resolve_tenant_session_bootstrap_mode
from kj_atlas_api.tenant_context import (
    SingleTenantContextResolver,
    TenantContextResolver,
)


_BUNDLE_STATE_KEY = "trusted_saas_runtime_adapters"
_STARTED_STATE_KEY = "_kj_atlas_runtime_started"


@dataclass(frozen=True, slots=True)
class TrustedSaasRuntimeAdapters:
    """Auth-edge adapters that must be installed as one pre-start bundle."""

    identity_context_resolver: SaasIdentityContextResolver
    tenant_context_resolver: TenantContextResolver
    active_tenant_session_persister: ActiveTenantSessionPersister

    def __post_init__(self) -> None:
        required_methods = (
            (self.identity_context_resolver, "resolve"),
            (self.tenant_context_resolver, "resolve"),
            (self.active_tenant_session_persister, "current_version"),
            (self.active_tenant_session_persister, "persist"),
        )
        if any(
            not callable(getattr(adapter, method, None)) for adapter, method in required_methods
        ):
            raise ValueError("trusted SaaS runtime adapter bundle is incomplete")


@dataclass(frozen=True, slots=True)
class TrustedSaasRuntimePolicy:
    """Validated non-secret settings required before a shared SaaS startup."""

    database_backend: str
    allow_jit_provisioning: bool
    access_control_adapter: str
    access_control_fail_safe_mode: str
    document_policy_binding_resolver: str
    tenant_capability_resolver: str

    def validate(self) -> None:
        requirements = (
            (self.database_backend == "postgresql", "PostgreSQL tenant DB guard"),
            (not self.allow_jit_provisioning, "disabled JIT provisioning"),
            (self.access_control_adapter == "external_http", "external access control"),
            (self.access_control_fail_safe_mode == "deny", "deny fail-safe mode"),
            (
                self.document_policy_binding_resolver == "external_http",
                "external document policy binding",
            ),
            (
                self.tenant_capability_resolver == "external_http",
                "external tenant capability resolution",
            ),
        )
        missing = [label for available, label in requirements if not available]
        if missing:
            raise RuntimeError("trusted SaaS runtime policy is incomplete: " + ", ".join(missing))


def _validate_saas_runtime_policy(runtime_policy: object) -> None:
    if not isinstance(runtime_policy, TrustedSaasRuntimePolicy):
        raise RuntimeError("trusted SaaS runtime policy is invalid")
    runtime_policy.validate()


def validate_trusted_saas_runtime_policy(
    *,
    runtime_profile: str,
    runtime_policy: TrustedSaasRuntimePolicy,
) -> None:
    """Reject an unsafe SaaS configuration before DB or adapter activation."""
    try:
        tenant_session_mode = resolve_tenant_session_bootstrap_mode(runtime_profile)
    except RuntimeError:
        raise RuntimeError("trusted SaaS runtime profile is invalid") from None
    if tenant_session_mode == "tenant-session-required":
        _validate_saas_runtime_policy(runtime_policy)


def install_trusted_saas_runtime(
    app: FastAPI,
    adapters: TrustedSaasRuntimeAdapters,
) -> None:
    """Install a complete trusted bundle before the application lifespan starts."""
    if not isinstance(adapters, TrustedSaasRuntimeAdapters):
        raise TypeError("trusted SaaS runtime adapters must use the validated bundle")
    if getattr(app.state, _STARTED_STATE_KEY, False):
        raise RuntimeError("trusted SaaS runtime adapters must be installed before startup")

    current = getattr(app.state, _BUNDLE_STATE_KEY, None)
    if current is not None and current is not adapters:
        raise RuntimeError("trusted SaaS runtime adapters cannot be replaced in-place")
    setattr(app.state, _BUNDLE_STATE_KEY, adapters)


def initialize_trusted_saas_runtime(
    app: FastAPI,
    *,
    runtime_profile: str,
    runtime_policy: TrustedSaasRuntimePolicy,
) -> bool:
    """Apply only a bundle whose tenant-session mode matches the runtime profile."""
    if getattr(app.state, _STARTED_STATE_KEY, False):
        raise RuntimeError("trusted SaaS runtime adapters are already initialized")

    try:
        tenant_session_mode = resolve_tenant_session_bootstrap_mode(runtime_profile)
    except RuntimeError:
        raise RuntimeError("trusted SaaS runtime profile is invalid") from None
    if tenant_session_mode == "tenant-session-required":
        _validate_saas_runtime_policy(runtime_policy)

    adapters = getattr(app.state, _BUNDLE_STATE_KEY, None)
    if adapters is not None and not isinstance(adapters, TrustedSaasRuntimeAdapters):
        raise RuntimeError("trusted SaaS runtime adapter bundle is invalid")
    if tenant_session_mode == "tenant-session-required" and adapters is None:
        raise RuntimeError("trusted SaaS runtime adapters are required by the runtime profile")
    if tenant_session_mode == "single-tenant" and adapters is not None:
        raise RuntimeError(
            "trusted SaaS runtime adapters cannot be enabled by a single-tenant profile"
        )

    app.state.saas_identity_context_resolver = None
    app.state.tenant_context_resolver = SingleTenantContextResolver()
    app.state.active_tenant_session_persister = None
    app.state.document_access_resource_resolver = SingleTenantHeaderResourceResolver()
    if adapters is not None:
        document_access_resource_resolver = ServerOwnedDocumentResourceResolver(
            policy_binding_resolver=build_document_policy_binding_resolver(),
        )
        app.state.saas_identity_context_resolver = adapters.identity_context_resolver
        app.state.tenant_context_resolver = adapters.tenant_context_resolver
        app.state.active_tenant_session_persister = adapters.active_tenant_session_persister
        app.state.document_access_resource_resolver = document_access_resource_resolver

    setattr(app.state, _STARTED_STATE_KEY, True)
    return adapters is not None


def release_trusted_saas_runtime(app: FastAPI) -> None:
    """Deactivate trusted adapters and release the guard after shutdown."""
    app.state.saas_identity_context_resolver = None
    app.state.tenant_context_resolver = SingleTenantContextResolver()
    app.state.active_tenant_session_persister = None
    app.state.document_access_resource_resolver = SingleTenantHeaderResourceResolver()
    setattr(app.state, _STARTED_STATE_KEY, False)
