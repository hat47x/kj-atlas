"""SAAS-TENANT-01 AC-7: authorization-surface capability separation."""

from __future__ import annotations

from kj_atlas_api.control_plane_auth import TENANT_PROVISION_CAPABILITY
from kj_atlas_api.routes.session import _session_response
from kj_atlas_api.session_context import (
    KNOWN_EFFECTIVE_CAPABILITIES,
    PLATFORM_CONTROL_PLANE_EFFECTIVE_CAPABILITIES,
    TENANT_ADMIN_EFFECTIVE_CAPABILITIES,
    WORKSPACE_EFFECTIVE_CAPABILITIES,
    WORKSPACE_SESSION_VISIBLE_CAPABILITIES,
    TenantSessionContext,
)
from kj_atlas_api.tenant_context import TenantContext, TenantSummary


def _trusted_session_with_all_capabilities() -> TenantSessionContext:
    tenant = TenantContext(
        tenant_id="tenant-a",
        membership_id="membership-a",
        resolved_by="verified_claim",
    )
    summary = TenantSummary(tenant_id="tenant-a", display_name="Tenant A")
    return TenantSessionContext(
        principal_id="user-1",
        tenant_context=tenant,
        active_tenant=summary,
        available_tenants=(summary,),
        effective_capabilities=tuple(sorted(KNOWN_EFFECTIVE_CAPABILITIES)),
        capability_version="capability-v1",
        tenant_session_version="session-v1",
    )


def test_capability_surfaces_are_disjoint_and_exhaustive() -> None:
    assert WORKSPACE_EFFECTIVE_CAPABILITIES.isdisjoint(
        TENANT_ADMIN_EFFECTIVE_CAPABILITIES
    )
    assert WORKSPACE_EFFECTIVE_CAPABILITIES.isdisjoint(
        PLATFORM_CONTROL_PLANE_EFFECTIVE_CAPABILITIES
    )
    assert TENANT_ADMIN_EFFECTIVE_CAPABILITIES.isdisjoint(
        PLATFORM_CONTROL_PLANE_EFFECTIVE_CAPABILITIES
    )
    assert (
        WORKSPACE_EFFECTIVE_CAPABILITIES
        | TENANT_ADMIN_EFFECTIVE_CAPABILITIES
        | PLATFORM_CONTROL_PLANE_EFFECTIVE_CAPABILITIES
    ) == KNOWN_EFFECTIVE_CAPABILITIES


def test_platform_capability_does_not_imply_document_read() -> None:
    assert TENANT_PROVISION_CAPABILITY in PLATFORM_CONTROL_PLANE_EFFECTIVE_CAPABILITIES
    assert "tenant.suspend" in PLATFORM_CONTROL_PLANE_EFFECTIVE_CAPABILITIES
    assert "document.read" in WORKSPACE_EFFECTIVE_CAPABILITIES
    assert "document.read" not in PLATFORM_CONTROL_PLANE_EFFECTIVE_CAPABILITIES


def test_workspace_session_visibility_excludes_platform_control_plane() -> None:
    assert WORKSPACE_SESSION_VISIBLE_CAPABILITIES == (
        WORKSPACE_EFFECTIVE_CAPABILITIES | TENANT_ADMIN_EFFECTIVE_CAPABILITIES
    )
    assert WORKSPACE_SESSION_VISIBLE_CAPABILITIES.isdisjoint(
        PLATFORM_CONTROL_PLANE_EFFECTIVE_CAPABILITIES
    )


def test_workspace_response_projects_platform_capabilities_without_mutating_session() -> None:
    trusted_session = _trusted_session_with_all_capabilities()

    response = _session_response(trusted_session)

    assert response.effectiveCapabilities == sorted(
        WORKSPACE_SESSION_VISIBLE_CAPABILITIES
    )
    assert "tenant.provision" not in response.effectiveCapabilities
    assert "tenant.suspend" not in response.effectiveCapabilities
    # Stage-B control-plane authorization consumes the trusted server-side
    # session, so projection must never strip the internal authorization input.
    assert "tenant.provision" in trusted_session.effective_capabilities
    assert "tenant.suspend" in trusted_session.effective_capabilities
