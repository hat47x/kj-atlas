from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from fastapi import HTTPException, Request
from sqlalchemy.orm import Session

from kj_atlas_api.auth_context import ResolvedIdentity, SaasIdentityContextResolver
from kj_atlas_api.session_context import (
    TenantCapabilityResolver,
    TenantSessionContext,
    build_tenant_session_context,
)
from kj_atlas_api.tenant_context import (
    SingleTenantContextResolver,
    TenantContext,
    TenantContextResolver,
)


@dataclass(frozen=True, slots=True)
class TrustedSaasRequestSession:
    identity: ResolvedIdentity
    tenant: TenantContext
    session: TenantSessionContext


def _error(*, status_code: int, code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail={"code": code, "message": message},
    )


def _canonical_identifier(value: object) -> bool:
    return bool(
        isinstance(value, str)
        and value
        and value.strip() == value
        and not any(ord(character) < 32 or ord(character) == 127 for character in value)
    )


def resolve_trusted_saas_request_session(
    *,
    request: Request,
    db: Session,
) -> TrustedSaasRequestSession:
    """Resolve one request exclusively from trusted identity, tenant and policy adapters."""
    identity_resolver = getattr(request.app.state, "saas_identity_context_resolver", None)
    if identity_resolver is None:
        raise _error(
            status_code=503,
            code="tenant_admin_auth_unavailable",
            message="Trusted SaaS identity resolution is unavailable.",
        )
    try:
        identity = cast(SaasIdentityContextResolver, identity_resolver).resolve(
            db=db,
            request=request,
        )
    except HTTPException:
        raise
    except Exception:
        raise _error(
            status_code=503,
            code="tenant_admin_auth_unavailable",
            message="Trusted SaaS identity resolution is unavailable.",
        ) from None
    try:
        principal_id = identity.user_id
    except Exception:
        raise _error(
            status_code=503,
            code="tenant_admin_auth_unavailable",
            message="Trusted SaaS identity resolution is unavailable.",
        ) from None
    if principal_id is None:
        raise _error(
            status_code=401,
            code="session_auth_required",
            message="Authenticated session context is required.",
        )
    if not _canonical_identifier(principal_id):
        raise _error(
            status_code=503,
            code="tenant_admin_auth_unavailable",
            message="Trusted SaaS identity resolution is unavailable.",
        )

    tenant_resolver: TenantContextResolver = getattr(
        request.app.state,
        "tenant_context_resolver",
        SingleTenantContextResolver(),
    )
    try:
        tenant = tenant_resolver.resolve(db=db, user_id=principal_id)
    except HTTPException:
        raise
    except Exception:
        raise _error(
            status_code=503,
            code="tenant_context_resolution_unavailable",
            message="Tenant context resolution is unavailable.",
        ) from None
    try:
        trusted_tenant = (
            tenant.resolved_by in {"verified_claim", "trusted_host_mapping"}
            and _canonical_identifier(tenant.tenant_id)
            and _canonical_identifier(tenant.membership_id)
        )
    except Exception:
        raise _error(
            status_code=503,
            code="tenant_context_resolution_unavailable",
            message="Tenant context resolution is unavailable.",
        ) from None
    if not trusted_tenant:
        raise _error(
            status_code=403,
            code="tenant_context_untrusted",
            message="Verified tenant context is required.",
        )

    capability_resolver = getattr(request.app.state, "tenant_capability_resolver", None)
    if capability_resolver is None:
        raise _error(
            status_code=503,
            code="capability_resolution_unavailable",
            message="Tenant capabilities are unavailable.",
        )
    session = build_tenant_session_context(
        db=db,
        principal_id=principal_id,
        tenant=tenant,
        capability_resolver=cast(TenantCapabilityResolver, capability_resolver),
    )
    return TrustedSaasRequestSession(
        identity=identity,
        tenant=session.tenant_context,
        session=session,
    )
