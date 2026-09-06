"""ADR-0080 guest invitation redeem boundary.

The opaque redeem state is host-created and is the sole source of tenant and
principal identity. External identity verification remains a separate trusted
adapter: this module accepts only its verified issuer/subject result and never a
member ``VerifiedTenantClaim``.
"""

from __future__ import annotations

import secrets
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from kj_atlas_api.auth_session_hash import derive_session_key_hash
from kj_atlas_api.guest_admission_models import GuestPrincipalRow
from kj_atlas_api.guest_admission_repository import GuestAdmissionError, GuestAdmissionRepository
from kj_atlas_api.guest_auth_state import create_guest_auth_session_in_transaction
from kj_atlas_api.guest_redeem_state_models import GuestRedeemStateRow
from kj_atlas_api.tenant_db_guard import apply_database_tenant_id

_REDEEM_STATE_LIFETIME = timedelta(minutes=15)
_REDEEM_STATE_DOMAIN = "guest-redeem-v1\x00"


class GuestRedeemError(ValueError):
    """Redeem state is invalid, stale, consumed, or cannot be activated."""


class GuestIdentityVerificationError(ValueError):
    """Trusted guest identity verification rejected the presented credential."""


class GuestIdentityVerificationUnavailableError(RuntimeError):
    """Trusted guest identity verification infrastructure is unavailable."""


@dataclass(frozen=True, slots=True)
class VerifiedGuestIdentity:
    issuer: str
    subject: str


@dataclass(frozen=True, slots=True)
class GuestRedeemChallenge:
    tenant_id: str
    guest_principal_id: str
    verification_method: str


class GuestIdentityVerifier(Protocol):
    def verify_identity(
        self, *, credential: str, verification_method: str
    ) -> VerifiedGuestIdentity: ...


def _utc(now: datetime | None = None) -> datetime:
    value = now or datetime.now(timezone.utc)
    if value.tzinfo is None or value.utcoffset() is None:
        raise GuestRedeemError("now must be timezone-aware")
    return value.astimezone(timezone.utc)


def _parse_timestamp(value: str) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed.astimezone(timezone.utc)


def _state_hash(raw_state: str, *, hash_key: bytes) -> str:
    if not raw_state or len(raw_state) > 256 or raw_state.strip() != raw_state:
        raise GuestRedeemError("redeem state is invalid")
    return derive_session_key_hash(_REDEEM_STATE_DOMAIN + raw_state, key=hash_key)


def _valid_state(row: GuestRedeemStateRow | None, *, now: datetime) -> GuestRedeemStateRow:
    if row is None or row.consumed_at is not None:
        raise GuestRedeemError("redeem state is invalid")
    expiry = _parse_timestamp(row.expires_at)
    if expiry is None or expiry <= now:
        raise GuestRedeemError("redeem state is invalid")
    return row


class DatabaseGuestRedeemStateStore:
    """Issue and redeem one-time invitation handles without client tenant input."""

    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory

    def issue_redeem_state(
        self,
        *,
        tenant_id: str,
        guest_principal_id: str,
        hash_key: bytes,
        now: datetime | None = None,
    ) -> str:
        current = _utc(now)
        raw_state = secrets.token_urlsafe(32)
        state_key_hash = _state_hash(raw_state, hash_key=hash_key)
        with self._session_factory() as db:
            apply_database_tenant_id(db=db, tenant_id=tenant_id)
            principal = db.get(GuestPrincipalRow, (tenant_id, guest_principal_id))
            if principal is None or principal.status != "pending" or principal.revoked_at is not None:
                raise GuestRedeemError("guest invitation is not redeemable")
            invitation_expiry = _parse_timestamp(principal.expires_at)
            if invitation_expiry is None or invitation_expiry <= current:
                raise GuestRedeemError("guest invitation is not redeemable")
            expires_at = min(current + _REDEEM_STATE_LIFETIME, invitation_expiry)
            db.add(
                GuestRedeemStateRow(
                    state_key_hash=state_key_hash,
                    tenant_id=tenant_id,
                    guest_principal_id=guest_principal_id,
                    created_at=current.isoformat(),
                    expires_at=expires_at.isoformat(),
                    consumed_at=None,
                )
            )
            db.commit()
        return raw_state

    def resolve_challenge(
        self,
        *,
        raw_state: str,
        hash_key: bytes,
        now: datetime | None = None,
    ) -> GuestRedeemChallenge:
        current = _utc(now)
        state_key_hash = _state_hash(raw_state, hash_key=hash_key)
        with self._session_factory() as db:
            row = _valid_state(db.get(GuestRedeemStateRow, state_key_hash), now=current)
            apply_database_tenant_id(db=db, tenant_id=row.tenant_id)
            principal = db.get(GuestPrincipalRow, (row.tenant_id, row.guest_principal_id))
            if principal is None or principal.status != "pending" or principal.revoked_at is not None:
                raise GuestRedeemError("redeem state is invalid")
            return GuestRedeemChallenge(
                tenant_id=row.tenant_id,
                guest_principal_id=row.guest_principal_id,
                verification_method=principal.verification_method,
            )

    def redeem_verified_identity(
        self,
        *,
        raw_state: str,
        hash_key: bytes,
        session_hash_key: bytes,
        identity: VerifiedGuestIdentity,
        now: datetime | None = None,
    ) -> str:
        """Atomically activate the principal, consume state, and mint a session."""
        current = _utc(now)
        state_key_hash = _state_hash(raw_state, hash_key=hash_key)
        raw_session_id = secrets.token_urlsafe(32)
        session_key_hash = derive_session_key_hash(raw_session_id, key=session_hash_key)
        with self._session_factory() as db:
            try:
                row = _valid_state(
                    db.scalar(
                        select(GuestRedeemStateRow)
                        .where(GuestRedeemStateRow.state_key_hash == state_key_hash)
                        .with_for_update()
                    ),
                    now=current,
                )
                apply_database_tenant_id(db=db, tenant_id=row.tenant_id)
                repo = GuestAdmissionRepository(db, tenant_id=row.tenant_id)
                repo.activate_verified_guest(
                    guest_principal_id=row.guest_principal_id,
                    verified_issuer=identity.issuer,
                    verified_subject=identity.subject,
                    redeemed_at=current.isoformat(),
                    now=current,
                )
                create_guest_auth_session_in_transaction(
                    db,
                    session_key_hash=session_key_hash,
                    tenant_id=row.tenant_id,
                    guest_principal_id=row.guest_principal_id,
                    issuer=identity.issuer,
                    subject=identity.subject,
                    now=current,
                )
                row.consumed_at = current.isoformat()
                db.commit()
            except (GuestAdmissionError, GuestRedeemError) as exc:
                db.rollback()
                raise GuestRedeemError("redeem state is invalid") from exc
            except Exception:
                db.rollback()
                raise
        return raw_session_id

    def preflight(self) -> None:
        with self._session_factory() as db:
            db.execute(select(GuestRedeemStateRow.state_key_hash).limit(1))
