from __future__ import annotations

from dataclasses import dataclass

from fastapi import FastAPI

from kj_atlas_api.active_tenant_session import ActiveTenantSessionPersister
from kj_atlas_api.auth_context import SaasIdentityContextResolver
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
            (self.active_tenant_session_persister, "persist"),
        )
        if any(not callable(getattr(adapter, method, None)) for adapter, method in required_methods):
            raise ValueError("trusted SaaS runtime adapter bundle is incomplete")


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


def initialize_trusted_saas_runtime(app: FastAPI) -> bool:
    """Apply the pre-installed bundle or the fail-closed single-tenant defaults."""
    if getattr(app.state, _STARTED_STATE_KEY, False):
        raise RuntimeError("trusted SaaS runtime adapters are already initialized")

    adapters = getattr(app.state, _BUNDLE_STATE_KEY, None)
    if adapters is not None and not isinstance(adapters, TrustedSaasRuntimeAdapters):
        raise RuntimeError("trusted SaaS runtime adapter bundle is invalid")

    app.state.saas_identity_context_resolver = None
    app.state.tenant_context_resolver = SingleTenantContextResolver()
    app.state.active_tenant_session_persister = None
    if adapters is not None:
        app.state.saas_identity_context_resolver = adapters.identity_context_resolver
        app.state.tenant_context_resolver = adapters.tenant_context_resolver
        app.state.active_tenant_session_persister = (
            adapters.active_tenant_session_persister
        )

    setattr(app.state, _STARTED_STATE_KEY, True)
    return adapters is not None


def release_trusted_saas_runtime(app: FastAPI) -> None:
    """Release the startup guard after lifespan shutdown."""
    setattr(app.state, _STARTED_STATE_KEY, False)
