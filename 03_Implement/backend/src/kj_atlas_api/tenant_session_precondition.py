from __future__ import annotations

from fastapi import HTTPException, Request

from kj_atlas_api.active_tenant_session import (
    require_current_tenant_session_version,
)
from kj_atlas_api.runtime_bootstrap import resolve_tenant_session_bootstrap_mode


TENANT_SESSION_VERSION_HEADER = "KJ-Atlas-Tenant-Session-Version"


def tenant_session_precondition_required(request: Request) -> bool:
    """Return whether tenant-scoped APIs require an active-session version."""
    try:
        runtime_profile = request.app.state.runtime_profile
        mode = resolve_tenant_session_bootstrap_mode(runtime_profile)
    except (AttributeError, RuntimeError):
        raise HTTPException(
            status_code=503,
            detail={
                "code": "runtime_policy_unavailable",
                "message": "Runtime policy is unavailable.",
            },
        ) from None
    return mode == "tenant-session-required"


def require_tenant_session_request_precondition(
    *,
    request: Request,
    current_version: str,
) -> None:
    """Check the opaque request version without exposing trusted session state.

    The caller must resolve the trusted identity and active tenant session before
    invoking this guard, and must invoke it before any tenant resource lookup.
    """
    if not tenant_session_precondition_required(request):
        return

    expected_versions = request.headers.getlist(TENANT_SESSION_VERSION_HEADER)
    expected_version = expected_versions[0] if len(expected_versions) == 1 else ""
    require_current_tenant_session_version(
        current_version=current_version,
        expected_version=expected_version,
    )
