"""ADR-0072: authorization for the control plane (`/admin/provision/**`).

SEC-ADMIN-PLANE-01 recorded two Critical findings that this module answers.

1. The provisioning surface had no authorization distinct from the business
   plane. Its only protection was the global `require_api_key` middleware, which
   passes through when `KJ_ATLAS_API_KEY` is unset and otherwise accepts the same
   shared static key used for the document and AI APIs. Since
   `POST /admin/provision/identity-providers` registers a trusted JWT issuer and
   its JWKS URI, anyone holding the business-plane key could register their own
   issuer and then authenticate as any user in any tenant.
2. `saas-multitenant` could not bootstrap at all: the surface returned 404 for
   any non-single-tenant profile, while the startup warning told the operator to
   call the very endpoint that 404s.

ADR-0072 adopted **D1=A+B** (two stages), **D2=A** (open the surface in SaaS and
protect it by authorization rather than by profile), and **D3=A** (fail-fast when
a production profile has no authentication configured; enforced in `settings.py`).

The two stages exist because bootstrap is a real state, not an edge case:

- **Stage A — control-plane bearer.** `KJ_ATLAS_ADMIN_API_KEY` presented as
  `X-Admin-Api-Key`. This is the only path that works while no identity provider
  is registered, which is exactly when `identity_providers` must be written.
  It is a static secret, so it identifies no subject and is bootstrap-only by
  intent.
- **Stage B — capability claim.** A verified trusted-SaaS session carrying the
  `tenant.provision` capability. This identifies a subject and lands in the audit
  trail, so it is the path for normal operation once an IdP exists.

Neither stage accepts the business-plane `X-Api-Key`. That separation is the
point of the issue.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from secrets import compare_digest
from typing import TYPE_CHECKING

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from kj_atlas_api.db import get_db
from kj_atlas_api.runtime_bootstrap import resolve_tenant_session_bootstrap_mode
from kj_atlas_api.settings import settings

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from kj_atlas_api.saas_request_context import TrustedSaasRequestSession

#: Header carrying the stage-A control-plane bearer. Distinct from `x-api-key`
#: so that a business-plane credential can never satisfy the control plane.
ADMIN_API_KEY_HEADER = "x-admin-api-key"

#: Capability required for stage B. Already part of
#: `session_context.KNOWN_EFFECTIVE_CAPABILITIES`.
TENANT_PROVISION_CAPABILITY = "tenant.provision"

#: Profiles where an unconfigured control plane stays open, preserving the
#: zero-configuration local experience. `settings.py` refuses to construct the
#: production profiles without `KJ_ATLAS_ADMIN_API_KEY` (D3=A), so a production
#: runtime can never reach the open branch.
_OPEN_WHEN_UNCONFIGURED_PROFILES = frozenset({"local-dev", "evaluation"})

_CONTROL_PLANE_SUBJECT_STATE = "kj_atlas_control_plane_subject"


@dataclass(frozen=True, slots=True)
class ControlPlaneSubject:
    """Trusted stage-B attribution carried from authorization to auditing."""

    principal_id: str
    tenant_id: str


def control_plane_subject(request: Request) -> ControlPlaneSubject | None:
    """Return server-resolved stage-B attribution, never caller headers."""
    subject = getattr(request.state, _CONTROL_PLANE_SUBJECT_STATE, None)
    return subject if isinstance(subject, ControlPlaneSubject) else None


def _unauthorized() -> HTTPException:
    # Deliberately identical for "no credential" and "wrong credential", and it
    # never echoes the presented value (settings._validate_canonical_bearer's
    # convention). The response must not reveal whether a key is configured.
    return HTTPException(
        status_code=401,
        detail={
            "code": "control_plane_unauthorized",
            "message": "Control plane authorization is required.",
        },
    )


def _matches_admin_bearer(request: Request) -> bool:
    configured = settings.admin_api_key
    if not configured:
        return False
    presented = request.headers.get(ADMIN_API_KEY_HEADER)
    if presented is None:
        return False
    normalized = presented.strip()
    if not normalized:
        return False
    return compare_digest(normalized, configured)


def _resolve_trusted_session(
    *, request: Request, db: Session
) -> TrustedSaasRequestSession | None:
    """Resolve a verified stage-B session when trusted adapters accept it.

    Imported lazily because the trusted-SaaS request context pulls in the
    adapter bundle, which is only installed for the SaaS profile.
    """
    try:
        from kj_atlas_api.saas_request_context import resolve_trusted_saas_request_session
    except Exception:  # pragma: no cover - bundle absent in single-tenant builds
        return None

    try:
        trusted_session = resolve_trusted_saas_request_session(request=request, db=db)
    except HTTPException:
        # No usable session (missing, untrusted, or precondition failed). Not an
        # error here: stage A may still authorize, and the caller raises 401.
        return None

    return trusted_session


def require_control_plane_authorization(
    request: Request,
    db: Session = Depends(get_db),
) -> None:
    """ADR-0072 D1=A+B / D2=A: authorize a control-plane request.

    Replaces `require_single_tenant_provisioning_surface`, which gated on the
    runtime profile rather than on authorization and therefore made SaaS
    bootstrap impossible (D2).
    """
    try:
        # Resolved for its validation side effect: an unknown profile must not
        # silently fall through to the open branch.
        resolve_tenant_session_bootstrap_mode(request.app.state.runtime_profile)
        profile = request.app.state.runtime_profile
    except (AttributeError, RuntimeError):
        raise HTTPException(
            status_code=503,
            detail={
                "code": "runtime_policy_unavailable",
                "message": "Runtime policy is unavailable.",
            },
        ) from None

    if _matches_admin_bearer(request):
        return

    trusted_session = _resolve_trusted_session(request=request, db=db)
    if trusted_session is not None:
        # SEC-ADMIN-PLANE-04: keep attribution in server-owned request state.
        # In particular, never accept X-Actor-Ref / X-Tenant-Id as audit truth.
        setattr(
            request.state,
            _CONTROL_PLANE_SUBJECT_STATE,
            ControlPlaneSubject(
                principal_id=trusted_session.session.principal_id,
                tenant_id=trusted_session.tenant.tenant_id,
            ),
        )
        if TENANT_PROVISION_CAPABILITY in trusted_session.session.effective_capabilities:
            return

    if settings.admin_api_key is None and profile in _OPEN_WHEN_UNCONFIGURED_PROFILES:
        # Development ergonomics only. Production profiles cannot reach here:
        # Settings() refuses to construct without the key (D3=A).
        return

    raise _unauthorized()
