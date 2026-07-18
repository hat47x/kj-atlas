from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from fastapi import HTTPException
from sqlalchemy.orm import Session

from kj_atlas_api.tenant_context import (
    TenantContext,
    TenantSummary,
    list_active_tenant_summaries,
    recheck_trusted_tenant_context,
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
MAX_SESSION_IDENTIFIER_LENGTH = 256
MAX_SESSION_DISPLAY_NAME_LENGTH = 256
MAX_SESSION_CAPABILITY_VERSION_LENGTH = 128
MAX_SESSION_CAPABILITY_LENGTH = 64
MAX_SESSION_TENANT_COUNT = 256
MAX_SESSION_RESPONSE_BYTES = 64 * 1024


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
    tenant_context: TenantContext
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


def _session_context_unavailable() -> None:
    raise HTTPException(
        status_code=503,
        detail={
            "code": "session_context_unavailable",
            "message": "Tenant session context is unavailable.",
        },
    )


def _canonical_value(value: object, *, max_length: int) -> str:
    if (
        not isinstance(value, str)
        or not value
        or len(value) > max_length
        or value.strip() != value
        or any(not character.isprintable() for character in value)
    ):
        raise ValueError("session context value is not canonical")
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
    try:
        principal_id = _canonical_value(
            principal_id,
            max_length=MAX_SESSION_IDENTIFIER_LENGTH,
        )
    except ValueError:
        _session_context_unavailable()

    tenant = recheck_trusted_tenant_context(
        db=db,
        user_id=principal_id,
        tenant=tenant,
    )
    available_tenants = list_active_tenant_summaries(
        db=db,
        user_id=principal_id,
        limit=MAX_SESSION_TENANT_COUNT + 1,
    )
    try:
        if not available_tenants or len(available_tenants) > MAX_SESSION_TENANT_COUNT:
            raise ValueError("session tenant count is invalid")
        tenant_ids: set[str] = set()
        for candidate in available_tenants:
            tenant_id = _canonical_value(
                candidate.tenant_id,
                max_length=MAX_SESSION_IDENTIFIER_LENGTH,
            )
            _canonical_value(
                candidate.display_name,
                max_length=MAX_SESSION_DISPLAY_NAME_LENGTH,
            )
            if tenant_id in tenant_ids:
                raise ValueError("session tenant ids must be unique")
            tenant_ids.add(tenant_id)
    except ValueError:
        _session_context_unavailable()
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
        capability_version = _canonical_value(
            snapshot.capability_version,
            max_length=MAX_SESSION_CAPABILITY_VERSION_LENGTH,
        )
        if (
            not isinstance(snapshot.effective_capabilities, tuple)
            or len(snapshot.effective_capabilities) > len(KNOWN_EFFECTIVE_CAPABILITIES)
        ):
            _capability_resolution_unavailable()
        effective_capabilities = tuple(
            sorted(
                _canonical_value(
                    capability,
                    max_length=MAX_SESSION_CAPABILITY_LENGTH,
                )
                for capability in snapshot.effective_capabilities
            )
        )
        if len(set(effective_capabilities)) != len(effective_capabilities):
            _capability_resolution_unavailable()
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
        tenant_context=tenant,
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
    try:
        requested_tenant_id = _canonical_value(
            requested_tenant_id,
            max_length=MAX_SESSION_IDENTIFIER_LENGTH,
        )
    except ValueError:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "tenant_not_available",
                "message": "Requested tenant is not available.",
            },
        ) from None
    if current_tenant.resolved_by == "verified_claim":
        resolved_by = "verified_claim"
    elif current_tenant.resolved_by == "trusted_host_mapping":
        resolved_by = "trusted_host_mapping"
    else:
        _tenant_context_untrusted()

    recheck_trusted_tenant_context(
        db=db,
        user_id=principal_id,
        tenant=current_tenant,
    )

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
