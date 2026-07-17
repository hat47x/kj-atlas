from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from fastapi import HTTPException
from sqlalchemy.orm import Session

from kj_atlas_api.tenant_context import (
    TenantContext,
    TenantSummary,
    list_active_tenant_summaries,
    select_active_tenant_context,
)


KNOWN_EFFECTIVE_CAPABILITIES = frozenset(
    {
        "document.read",
        "document.write",
        "document.export",
        "document.share",
        "document.policy.manage",
        "membership.provision",
        "agent.register",
        "agent.revoke",
        "audit.read",
        "tenant.provision",
        "tenant.suspend",
    }
)


@dataclass(frozen=True, slots=True)
class CapabilitySnapshot:
    effective_capabilities: tuple[str, ...]
    capability_version: str


class TenantCapabilityResolver(Protocol):
    """Resolve capabilities from a trusted policy source for one tenant context."""

    def resolve(
        self,
        *,
        db: Session,
        principal_id: str,
        tenant: TenantContext,
    ) -> CapabilitySnapshot:
        ...


@dataclass(frozen=True, slots=True)
class TenantSessionContext:
    principal_id: str
    active_tenant: TenantSummary
    available_tenants: tuple[TenantSummary, ...]
    effective_capabilities: tuple[str, ...]
    capability_version: str


def _session_auth_required() -> None:
    raise HTTPException(
        status_code=401,
        detail={
            "code": "session_auth_required",
            "message": "Authenticated session context is required.",
        },
    )


def _tenant_context_untrusted() -> None:
    raise HTTPException(
        status_code=403,
        detail={
            "code": "tenant_context_untrusted",
            "message": "Verified tenant context is required.",
        },
    )


def _capability_resolution_unavailable() -> None:
    raise HTTPException(
        status_code=503,
        detail={
            "code": "capability_resolution_unavailable",
            "message": "Tenant capabilities are unavailable.",
        },
    )


def _normalize_canonical_value(value: str) -> str:
    if not value or value.strip() != value or any(
        ord(character) < 32 or ord(character) == 127 for character in value
    ):
        _capability_resolution_unavailable()
    return value


def build_tenant_session_context(
    *,
    db: Session,
    principal_id: str | None,
    tenant: TenantContext,
    capability_resolver: TenantCapabilityResolver,
) -> TenantSessionContext:
    """Build a session payload only from rechecked membership and trusted policy data."""
    if principal_id is None:
        _session_auth_required()

    available_tenants = list_active_tenant_summaries(db=db, user_id=principal_id)
    active_tenant = next(
        (candidate for candidate in available_tenants if candidate.tenant_id == tenant.tenant_id),
        None,
    )
    if active_tenant is None:
        _tenant_context_untrusted()

    try:
        snapshot = capability_resolver.resolve(
            db=db,
            principal_id=principal_id,
            tenant=tenant,
        )
        capability_version = _normalize_canonical_value(snapshot.capability_version)
        effective_capabilities = tuple(
            sorted(
                {
                    _normalize_canonical_value(capability)
                    for capability in snapshot.effective_capabilities
                }
            )
        )
        if any(
            capability not in KNOWN_EFFECTIVE_CAPABILITIES
            for capability in effective_capabilities
        ):
            _capability_resolution_unavailable()
    except HTTPException:
        raise
    except Exception:
        _capability_resolution_unavailable()

    return TenantSessionContext(
        principal_id=principal_id,
        active_tenant=active_tenant,
        available_tenants=available_tenants,
        effective_capabilities=effective_capabilities,
        capability_version=capability_version,
    )


def switch_tenant_session_context(
    *,
    db: Session,
    principal_id: str | None,
    current_tenant: TenantContext,
    requested_tenant_id: str,
    capability_resolver: TenantCapabilityResolver,
) -> TenantSessionContext:
    """Recheck current context and requested tenant before resolving new capabilities."""
    if principal_id is None:
        _session_auth_required()
    if current_tenant.resolved_by == "verified_claim":
        resolved_by = "verified_claim"
    elif current_tenant.resolved_by == "trusted_host_mapping":
        resolved_by = "trusted_host_mapping"
    else:
        _tenant_context_untrusted()

    available_tenants = list_active_tenant_summaries(db=db, user_id=principal_id)
    if not any(tenant.tenant_id == current_tenant.tenant_id for tenant in available_tenants):
        _tenant_context_untrusted()

    selected_tenant = select_active_tenant_context(
        db=db,
        user_id=principal_id,
        tenant_id=requested_tenant_id,
        resolved_by=resolved_by,
    )
    return build_tenant_session_context(
        db=db,
        principal_id=principal_id,
        tenant=selected_tenant,
        capability_resolver=capability_resolver,
    )
