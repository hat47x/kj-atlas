from __future__ import annotations

from dataclasses import dataclass

from fastapi import FastAPI

from kj_atlas_api.access_control import (
    AccessControlAdapter,
    ExternalPolicyAccessControlAdapter,
)
from kj_atlas_api.active_tenant_session import ActiveTenantSessionPersister
from kj_atlas_api.auth_context import SaasIdentityContextResolver
from kj_atlas_api.document_access_resource import (
    DocumentPolicyBindingResolver,
    ServerOwnedDocumentResourceResolver,
    SingleTenantHeaderResourceResolver,
)
from kj_atlas_api.document_policy_binding import ExternalHttpDocumentPolicyBindingResolver
from kj_atlas_api.runtime_bootstrap import resolve_tenant_session_bootstrap_mode
from kj_atlas_api.session_context import TenantCapabilityResolver
from kj_atlas_api.tenant_capability import ExternalHttpTenantCapabilityResolver
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
            (self.active_tenant_session_persister, "clear"),
        )
        if any(
            not callable(getattr(adapter, method, None)) for adapter, method in required_methods
        ):
            raise ValueError("trusted SaaS runtime adapter bundle is incomplete")


@dataclass(frozen=True, slots=True)
class TrustedSaasRuntimePolicy:
    """Validated non-secret settings required before a shared SaaS startup.

    ADR-0063 D9-6: includes auth-edge-side checks (JWT algorithms,
    tenant claim name, mode). Active identity_providers rows are
    checked post-DB-init in _validate_saas_providers_exist().
    """

    database_backend: str
    allow_jit_provisioning: bool
    access_control_adapter: str
    access_control_fail_safe_mode: str
    document_policy_binding_resolver: str
    tenant_capability_resolver: str
    # ADR-0063 D9-6: JWT auth-edge settings
    jwt_algorithms: str = "RS256,ES256"
    tenant_claim_name: str = "tenant_ref"

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
            # ADR-0063 D9-6: JWT algorithms must be non-empty (Settings already
            # validates no-HMAC, known-algorithms-only, but cross-check here).
            (bool(self.jwt_algorithms.strip()), "JWT algorithm allowlist set"),
            (bool(self.tenant_claim_name.strip()), "tenant claim name set"),
        )
        missing = [label for available, label in requirements if not available]
        if missing:
            raise RuntimeError("trusted SaaS runtime policy is incomplete: " + ", ".join(missing))


@dataclass(frozen=True, slots=True)
class TrustedSaasRuntimeComponents:
    """Concrete policy components built before database initialization."""

    access_control_adapter: AccessControlAdapter
    tenant_capability_resolver: TenantCapabilityResolver
    document_policy_binding_resolver: DocumentPolicyBindingResolver

    def validate_for_saas(self) -> None:
        requirements = (
            (
                isinstance(
                    self.access_control_adapter,
                    ExternalPolicyAccessControlAdapter,
                ),
                "external access-control component",
            ),
            (
                isinstance(
                    self.tenant_capability_resolver,
                    ExternalHttpTenantCapabilityResolver,
                ),
                "external tenant capability component",
            ),
            (
                isinstance(
                    self.document_policy_binding_resolver,
                    ExternalHttpDocumentPolicyBindingResolver,
                ),
                "external document binding component",
            ),
        )
        missing = [label for available, label in requirements if not available]
        if missing:
            raise RuntimeError(
                "trusted SaaS runtime components are incomplete: " + ", ".join(missing)
            )


def _validate_saas_runtime_policy(runtime_policy: object) -> None:
    if not isinstance(runtime_policy, TrustedSaasRuntimePolicy):
        raise RuntimeError("trusted SaaS runtime policy is invalid")
    runtime_policy.validate()


def _validate_runtime_components(
    runtime_components: object,
    *,
    tenant_session_mode: str,
) -> TrustedSaasRuntimeComponents:
    if not isinstance(runtime_components, TrustedSaasRuntimeComponents):
        raise RuntimeError("trusted SaaS runtime components are invalid")
    if tenant_session_mode == "tenant-session-required":
        runtime_components.validate_for_saas()
    return runtime_components


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


def _trusted_saas_runtime_preflight(
    app: FastAPI,
    *,
    runtime_profile: str,
    runtime_policy: TrustedSaasRuntimePolicy,
    runtime_components: TrustedSaasRuntimeComponents,
) -> tuple[str, TrustedSaasRuntimeAdapters | None]:
    if getattr(app.state, _STARTED_STATE_KEY, False):
        raise RuntimeError("trusted SaaS runtime adapters are already initialized")
    try:
        tenant_session_mode = resolve_tenant_session_bootstrap_mode(runtime_profile)
    except RuntimeError:
        raise RuntimeError("trusted SaaS runtime profile is invalid") from None
    if tenant_session_mode == "tenant-session-required":
        _validate_saas_runtime_policy(runtime_policy)
    _validate_runtime_components(
        runtime_components,
        tenant_session_mode=tenant_session_mode,
    )

    adapters = getattr(app.state, _BUNDLE_STATE_KEY, None)
    if adapters is not None and not isinstance(adapters, TrustedSaasRuntimeAdapters):
        raise RuntimeError("trusted SaaS runtime adapter bundle is invalid")
    if tenant_session_mode == "tenant-session-required" and adapters is None:
        raise RuntimeError("trusted SaaS runtime adapters are required by the runtime profile")
    if tenant_session_mode == "single-tenant" and adapters is not None:
        raise RuntimeError(
            "trusted SaaS runtime adapters cannot be enabled by a single-tenant profile"
        )
    return tenant_session_mode, adapters


def validate_trusted_saas_runtime_preflight(
    app: FastAPI,
    *,
    runtime_profile: str,
    runtime_policy: TrustedSaasRuntimePolicy,
    runtime_components: TrustedSaasRuntimeComponents,
) -> None:
    """Validate profile, policy and bundle without changing application state."""
    _trusted_saas_runtime_preflight(
        app,
        runtime_profile=runtime_profile,
        runtime_policy=runtime_policy,
        runtime_components=runtime_components,
    )


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
    runtime_components: TrustedSaasRuntimeComponents,
) -> bool:
    """Apply only a bundle whose tenant-session mode matches the runtime profile."""
    _, adapters = _trusted_saas_runtime_preflight(
        app,
        runtime_profile=runtime_profile,
        runtime_policy=runtime_policy,
        runtime_components=runtime_components,
    )

    app.state.saas_identity_context_resolver = None
    app.state.tenant_context_resolver = SingleTenantContextResolver()
    app.state.active_tenant_session_persister = None
    app.state.document_access_resource_resolver = SingleTenantHeaderResourceResolver()
    if adapters is not None:
        document_access_resource_resolver = ServerOwnedDocumentResourceResolver(
            policy_binding_resolver=runtime_components.document_policy_binding_resolver,
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


def validate_saas_providers_exist() -> None:
    """ADR-0063 D9-6: post-DB-init check that at least one active identity
    provider with a JWKS URI is registered.

    Called after database initialization in the lifespan. Logs a warning
    rather than blocking startup, so that the admin API can be used to
    register the first provider (chicken-and-egg problem).
    """
    import logging

    from kj_atlas_api.models import IdentityProviderRow

    logger = logging.getLogger(__name__)
    try:
        from kj_atlas_api.db import SessionLocal

        db = SessionLocal()
        try:
            count = (
                db.query(IdentityProviderRow)
                .filter(
                    IdentityProviderRow.lifecycle_state == "active",
                    IdentityProviderRow.jwks_uri.isnot(None),
                )
                .count()
            )
            if count == 0:
                # SEC-ADMIN-PLANE-01 AC-4: this warning previously named an
                # endpoint that returned 404 on this very profile. ADR-0072 D2=A
                # opened the surface and replaced the profile gate with
                # authorization, so the instruction is now reachable -- but only
                # with the control-plane credential, which the text must say.
                logger.warning(
                    "SaaS profile: no active identity providers with JWKS URI "
                    "found. Register at least one via "
                    "POST /admin/provision/identity-providers, presenting the "
                    "control-plane credential as the X-Admin-Api-Key header "
                    "(KJ_ATLAS_ADMIN_API_KEY). The business-plane key is not "
                    "accepted. Authentication requests fail until an identity "
                    "provider exists."
                )
        finally:
            db.close()
    except Exception:
        logger.warning(
            "SaaS profile: could not check identity_providers table "
            "(database may not be ready).",
            exc_info=True,
        )
