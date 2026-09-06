"""ADR-0080 D1 guest identity verification adapter.

The adapter reuses the hardened configured OIDC JWT/JWKS verifier but stops
before member provisioning and receiving-tenant IdP trust.  A guest therefore
proves an external identity without becoming a TenantMembership row or relying
on TenantIdentityProviderRow.
"""

from __future__ import annotations

import logging
from collections.abc import Callable

from sqlalchemy.orm import Session

from kj_atlas_api.guest_redeem import (
    GuestIdentityVerificationError,
    GuestIdentityVerificationUnavailableError,
    VerifiedGuestIdentity,
)
from kj_atlas_api.jwks_store import JwksStore
from kj_atlas_api.trusted_auth_edge import JwtIdentityError, verify_configured_oidc_token

logger = logging.getLogger(__name__)
_ALLOWED_VERIFICATION_METHODS = frozenset({"home_org_idp", "personal_account"})


class DatabaseJwtGuestIdentityVerifier:
    """Verify guest OIDC/broker JWTs without resolving member tenant context."""

    def __init__(
        self,
        *,
        session_factory: Callable[[], Session],
        jwks_store: JwksStore,
    ) -> None:
        self._session_factory = session_factory
        self._jwks_store = jwks_store

    def verify_identity(
        self,
        *,
        credential: str,
        verification_method: str,
    ) -> VerifiedGuestIdentity:
        if verification_method not in _ALLOWED_VERIFICATION_METHODS:
            raise GuestIdentityVerificationError("unsupported guest verification method")
        token = credential.strip()
        if not token or token != credential:
            raise GuestIdentityVerificationError("invalid guest identity credential")

        try:
            with self._session_factory() as db:
                verified = verify_configured_oidc_token(
                    db=db,
                    token=token,
                    jwks_store=self._jwks_store,
                )
        except JwtIdentityError as exc:
            if exc.status_code >= 500:
                logger.warning("guest identity provider verification unavailable")
                raise GuestIdentityVerificationUnavailableError(
                    "guest identity provider verification unavailable"
                ) from None
            logger.info("guest identity verification rejected")
            raise GuestIdentityVerificationError("guest identity verification failed") from None

        return VerifiedGuestIdentity(
            issuer=verified.provider.issuer,
            subject=verified.subject,
        )
