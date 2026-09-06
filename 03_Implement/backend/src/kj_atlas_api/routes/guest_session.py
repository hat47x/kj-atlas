from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from kj_atlas_api.active_tenant_session import tenant_session_cookie_is_secure
from kj_atlas_api.guest_redeem import (
    GuestIdentityVerificationError,
    GuestRedeemError,
)
from kj_atlas_api.guest_request_auth import GUEST_AUTH_SESSION_COOKIE

router = APIRouter(prefix="/session/guest", tags=["guest-session"])
_GUEST_SESSION_MAX_AGE_SECONDS = 12 * 60 * 60


class GuestRedeemRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    state: str = Field(min_length=16, max_length=256)
    identity_credential: str = Field(alias="identityCredential", min_length=1, max_length=8192)


@router.post("/redeem")
def redeem_guest_session(payload: GuestRedeemRequest, request: Request) -> JSONResponse:
    """Exchange a host-bound redeem state plus trusted identity proof for a guest session.

    Tenant/principal are deliberately absent from the request schema. They are
    recovered only from the one-time state. The verifier is a guest-specific
    trusted adapter and must not return a member VerifiedTenantClaim.
    """
    store = getattr(request.app.state, "guest_redeem_state_store", None)
    verifier = getattr(request.app.state, "guest_identity_verifier", None)
    state_hash_key = getattr(request.app.state, "guest_redeem_state_hash_key", None)
    session_hash_key = getattr(request.app.state, "guest_auth_session_hash_key", None)
    if store is None or verifier is None or state_hash_key is None or session_hash_key is None:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "guest_redeem_unavailable",
                "message": "Guest sign-in is unavailable.",
            },
        )

    try:
        challenge = store.resolve_challenge(
            raw_state=payload.state,
            hash_key=state_hash_key,
        )
        identity = verifier.verify_identity(
            credential=payload.identity_credential,
            verification_method=challenge.verification_method,
        )
        raw_session_id = store.redeem_verified_identity(
            raw_state=payload.state,
            hash_key=state_hash_key,
            session_hash_key=session_hash_key,
            identity=identity,
        )
    except (GuestRedeemError, GuestIdentityVerificationError):
        raise HTTPException(
            status_code=401,
            detail={"code": "guest_redeem_invalid", "message": "Guest sign-in failed."},
        ) from None
    except Exception:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "guest_redeem_persistence_failed",
                "message": "Guest sign-in could not be completed.",
            },
        ) from None

    runtime_profile = getattr(request.app.state, "runtime_profile", "local-dev")
    response = JSONResponse(
        status_code=200,
        content={"status": "redeemed"},
        headers={"Cache-Control": "no-store", "Pragma": "no-cache"},
    )
    response.set_cookie(
        key=GUEST_AUTH_SESSION_COOKIE,
        value=raw_session_id,
        httponly=True,
        secure=tenant_session_cookie_is_secure(runtime_profile),
        samesite="strict",
        max_age=_GUEST_SESSION_MAX_AGE_SECONDS,
        path="/",
    )
    return response
