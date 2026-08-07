"""ADR-0063 D9-3: concrete SaasIdentityContextResolver using JWT bearer tokens.

Deployment auth edge (identity broker / IdP) issues a signed JWT. This module
verifies the token, resolves the subject to a kj-atlas user, and returns a
ResolvedIdentity carrying the VerifiedTenantClaim for downstream tenant
resolution.

JWT requirements (ADR-0063 D2/D4):
- Algorithm allowlist: RS256, ES256 only. HMAC and 'none' are always rejected.
- Token header jku/x5u/embedded key references are never followed.
- kid is resolved from the fetched JWK set only.
- Clock skew tolerance: 60 seconds (fixed, not configurable).
- exp/iss/aud/alg validation is enforced on every call.
"""

from __future__ import annotations

from dataclasses import dataclass

import jwt
from fastapi import Request
from sqlalchemy.orm import Session

from kj_atlas_api.auth_context import AuthContext, ResolvedIdentity
from kj_atlas_api.jwks_store import JwksStore
from kj_atlas_api.models import IdentityProviderRow

# ADR-0063 D4: algorithm allowlist (RS256, ES256). HMAC and 'none' rejected.
_JWT_ALGORITHMS = frozenset({"RS256", "ES256"})
# ADR-0063 D4: clock skew 60 seconds fixed.
_JWT_CLOCK_SKEW_SECONDS = 60

# Header name carrying the JWT bearer token (ADR-0020 §3-2 jwt_header mode).
_JWT_HEADER = "X-Kj-Atlas-Authorization"


def _extract_bearer_token(request: Request) -> str | None:
    """Extract a bearer token from the configured header."""
    raw = request.headers.get(_JWT_HEADER)
    if raw is None:
        return None
    value = raw.strip()
    if not value:
        return None
    if value.lower().startswith("bearer "):
        return value[7:].strip()
    return value


@dataclass(frozen=True, slots=True)
class JwtIdentityError(Exception):
    """Identity layer error — opaque to the caller (ADR-0063 D6)."""

    status_code: int
    code: str


def _resolve_identity_provider(db: Session, issuer: str, audience: str) -> IdentityProviderRow | None:
    """Look up an active identity provider by issuer + audience."""
    return (
        db.query(IdentityProviderRow)
        .filter(
            IdentityProviderRow.issuer == issuer,
            IdentityProviderRow.audience == audience,
            IdentityProviderRow.lifecycle_state == "active",
            IdentityProviderRow.protocol.in_({"oidc"}),
        )
        .one_or_none()
    )


def _verify_jwt(
    token: str,
    jwks_keys: list[dict[str, object]],
    issuer: str,
    audience: str,
) -> dict[str, object]:
    """Verify a JWT token against the given JWK set and expected issuer/audience.

    Raises JwtIdentityError on any verification failure.
    """
    try:
        # jwt.decode() with algorithms= rejects 'none' and HMAC automatically.
        return jwt.decode(
            token,
            key=jwt.PyJWKSet.from_dict({"keys": jwks_keys}),
            algorithms=list(_JWT_ALGORITHMS),
            issuer=issuer,
            audience=audience,
            options={
                "require": ["exp", "iss", "aud", "sub"],
                "verify_signature": True,
                "verify_exp": True,
                "verify_iss": True,
                "verify_aud": True,
            },
            leeway=_JWT_CLOCK_SKEW_SECONDS,
        )
    except jwt.ExpiredSignatureError:
        raise JwtIdentityError(status_code=401, code="token_expired") from None
    except jwt.InvalidIssuerError:
        raise JwtIdentityError(status_code=401, code="invalid_issuer") from None
    except jwt.InvalidAudienceError:
        raise JwtIdentityError(status_code=401, code="invalid_audience") from None
    except jwt.InvalidSignatureError:
        raise JwtIdentityError(status_code=401, code="invalid_signature") from None
    except jwt.PyJWTError:
        raise JwtIdentityError(status_code=401, code="invalid_token") from None


def _resolve_subject_to_user_id(db: Session, provider_id: str, subject: str) -> str | None:
    """Map (identity_provider_id, subject) → user_id via user_identities."""
    from kj_atlas_api.models import UserIdentityRow

    row = (
        db.query(UserIdentityRow)
        .filter(
            UserIdentityRow.identity_provider_id == provider_id,
            UserIdentityRow.subject == subject,
        )
        .one_or_none()
    )
    return row.user_id if row is not None else None


class JwtSaasIdentityContextResolver:
    """ADR-0063 D9-3: concrete identity resolver for saas-multitenant.

    Verifies a JWT bearer token against the configured identity provider's JWKS,
    resolves the token subject to a kj-atlas user, and returns a ResolvedIdentity.
    """

    def __init__(self, *, jwks_store: JwksStore):
        self._jwks = jwks_store

    def resolve(self, *, db: Session, request: Request) -> ResolvedIdentity:
        """Verify the bearer token and resolve to a kj-atlas identity.

        Raises JwtIdentityError (→ 401) when the token is missing, invalid, or
        the subject is not provisioned.
        """
        token = _extract_bearer_token(request)
        if token is None:
            raise JwtIdentityError(status_code=401, code="missing_token")

        # Peek at issuer / audience without trusting the signature yet.
        try:
            claims_unverified: dict[str, object] = jwt.decode(
                token,
                options={"verify_signature": False},
                algorithms=list(_JWT_ALGORITHMS),
            )
        except jwt.PyJWTError:
            raise JwtIdentityError(status_code=401, code="invalid_token") from None

        issuer = claims_unverified.get("iss")
        audience = claims_unverified.get("aud")
        if not isinstance(issuer, str) or not isinstance(audience, str):
            raise JwtIdentityError(status_code=401, code="invalid_token")

        provider = _resolve_identity_provider(db, issuer, audience)
        if provider is None:
            raise JwtIdentityError(status_code=401, code="unknown_provider")

        # Fetch JWKS and verify with signature.
        keys = self._fetch_jwks_keys(provider)

        verified = _verify_jwt(token, keys, issuer, audience)
        subject = verified.get("sub")
        if not isinstance(subject, str):
            raise JwtIdentityError(status_code=401, code="invalid_token")

        user_id = _resolve_subject_to_user_id(db, provider.id, subject)
        if user_id is None:
            raise JwtIdentityError(status_code=403, code="identity_not_provisioned")

        return ResolvedIdentity(
            user_id=user_id,
            reviewer_ref=user_id,
            owner_ref=user_id,
            auth_context=AuthContext(
                actor_ref=user_id,
                user_id=user_id,
                provider=provider.id,
                external_uid=subject,
            ),
        )

    def _fetch_jwks_keys(self, provider: IdentityProviderRow) -> list[dict[str, object]]:
        """Return cached or freshly fetched JWKS keys for the provider."""
        if not self._jwks.needs_refresh(provider.id):
            cached = self._jwks.get(provider.id)
            if cached is not None:
                return cached

        # Cooldown guard: if we failed recently and cooldown hasn't elapsed, reuse stale.
        if not self._jwks.can_force_refresh(provider.id):
            stale = self._jwks.get(provider.id)
            if stale is not None:
                return stale
            raise JwtIdentityError(status_code=503, code="jwks_unavailable")

        try:
            keys = _fetch_jwks(provider.jwks_uri)
            self._jwks.set(provider.id, keys)
            return keys
        except OSError:
            self._jwks.set_fresh_failure(provider.id)
            stale = self._jwks.get(provider.id)
            if stale is not None:
                return stale
            raise JwtIdentityError(status_code=503, code="jwks_unavailable") from None


def _fetch_jwks(jwks_uri: str | None) -> list[dict[str, object]]:
    """Fetch and parse a JWKS endpoint. jwks_uri must be validated at write time."""
    import json

    import httpx

    if not jwks_uri:
        raise JwtIdentityError(status_code=503, code="jwks_unavailable")

    try:
        response = httpx.get(jwks_uri, timeout=10.0)
        response.raise_for_status()
        data = json.loads(response.text)
    except (httpx.HTTPError, json.JSONDecodeError, OSError):
        raise JwtIdentityError(status_code=503, code="jwks_unavailable") from None

    if not isinstance(data, dict) or not isinstance(data.get("keys"), list):
        raise JwtIdentityError(status_code=503, code="jwks_unavailable")

    keys: list[dict[str, object]] = data["keys"]
    if not keys:
        raise JwtIdentityError(status_code=503, code="jwks_unavailable")
    return keys
