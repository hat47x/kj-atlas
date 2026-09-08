"""Server-owned authentication state for ADR-0080 guest principals."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from kj_atlas_api.guest_admission_models import GuestPrincipalRow
from kj_atlas_api.guest_auth_session_models import GuestAuthSessionRow
from kj_atlas_api.tenant_db_guard import apply_database_tenant_id


_ABSOLUTE_SESSION_LIFETIME = timedelta(hours=12)
_IDLE_TIMEOUT = timedelta(minutes=60)


def _parse_iso(value: str) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed.astimezone(timezone.utc)


@dataclass(frozen=True, slots=True)
class ResolvedGuestAuthSession:
    tenant_id: str
    guest_principal_id: str
    issuer: str
    subject: str


class GuestAuthSessionError(ValueError):
    """Rejected creation of a server-owned guest session."""


class DatabaseGuestAuthSessionStore:
    """Resolve a pre-tenant cookie without turning a guest into a member.

    The session row itself is pre-tenant authentication state.  After it yields
    a tenant id, this store immediately applies the transaction-local tenant
    guard before consulting ``guest_principals``.  A live cookie therefore
    still fails closed after principal revocation or any identity mismatch.
    """

    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory

    @staticmethod
    def _require_verified_principal(
        db: Session,
        *,
        tenant_id: str,
        guest_principal_id: str,
        issuer: str,
        subject: str,
    ) -> GuestPrincipalRow:
        apply_database_tenant_id(db=db, tenant_id=tenant_id)
        principal = db.get(GuestPrincipalRow, (tenant_id, guest_principal_id))
        if (
            principal is None
            or principal.status != "active"
            or principal.revoked_at is not None
            or principal.verified_issuer != issuer
            or principal.verified_subject != subject
        ):
            raise GuestAuthSessionError("guest principal identity is not active and verified")
        return principal

    def create_guest_auth_session(
        self,
        *,
        session_key_hash: str,
        tenant_id: str,
        guest_principal_id: str,
        issuer: str,
        subject: str,
    ) -> None:
        now = datetime.now(timezone.utc)
        with self._session_factory() as db:
            self._require_verified_principal(
                db,
                tenant_id=tenant_id,
                guest_principal_id=guest_principal_id,
                issuer=issuer,
                subject=subject,
            )
            db.add(
                GuestAuthSessionRow(
                    session_key_hash=session_key_hash,
                    tenant_id=tenant_id,
                    guest_principal_id=guest_principal_id,
                    issuer=issuer,
                    subject=subject,
                    created_at=now.isoformat(),
                    last_used_at=now.isoformat(),
                    absolute_expires_at=(now + _ABSOLUTE_SESSION_LIFETIME).isoformat(),
                    revoked_at=None,
                )
            )
            db.commit()

    def resolve_guest_auth_session(
        self, *, session_key_hash: str
    ) -> ResolvedGuestAuthSession | None:
        now = datetime.now(timezone.utc)
        with self._session_factory() as db:
            row = db.get(GuestAuthSessionRow, session_key_hash)
            if row is None or row.revoked_at is not None:
                return None
            absolute_expiry = _parse_iso(row.absolute_expires_at)
            last_used = _parse_iso(row.last_used_at)
            if absolute_expiry is None or absolute_expiry <= now:
                return None
            if last_used is None or last_used + _IDLE_TIMEOUT <= now:
                return None
            try:
                self._require_verified_principal(
                    db,
                    tenant_id=row.tenant_id,
                    guest_principal_id=row.guest_principal_id,
                    issuer=row.issuer,
                    subject=row.subject,
                )
            except GuestAuthSessionError:
                return None
            resolved = ResolvedGuestAuthSession(
                tenant_id=row.tenant_id,
                guest_principal_id=row.guest_principal_id,
                issuer=row.issuer,
                subject=row.subject,
            )
            row.last_used_at = now.isoformat()
            db.commit()
            return resolved

    def revoke_guest_auth_session(self, *, session_key_hash: str) -> None:
        with self._session_factory() as db:
            db.execute(
                update(GuestAuthSessionRow)
                .where(GuestAuthSessionRow.session_key_hash == session_key_hash)
                .values(revoked_at=datetime.now(timezone.utc).isoformat())
            )
            db.commit()

    def preflight(self) -> None:
        with self._session_factory() as db:
            db.execute(select(GuestAuthSessionRow.session_key_hash).limit(1))


def create_guest_auth_session_in_transaction(
    db: Session,
    *,
    session_key_hash: str,
    tenant_id: str,
    guest_principal_id: str,
    issuer: str,
    subject: str,
    now: datetime | None = None,
) -> None:
    """Insert a guest auth session without committing the caller transaction."""
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None or current.utcoffset() is None:
        raise GuestAuthSessionError("now must be timezone-aware")
    current = current.astimezone(timezone.utc)
    DatabaseGuestAuthSessionStore._require_verified_principal(
        db,
        tenant_id=tenant_id,
        guest_principal_id=guest_principal_id,
        issuer=issuer,
        subject=subject,
    )
    db.add(
        GuestAuthSessionRow(
            session_key_hash=session_key_hash,
            tenant_id=tenant_id,
            guest_principal_id=guest_principal_id,
            issuer=issuer,
            subject=subject,
            created_at=current.isoformat(),
            last_used_at=current.isoformat(),
            absolute_expires_at=(current + _ABSOLUTE_SESSION_LIFETIME).isoformat(),
            revoked_at=None,
        )
    )
    db.flush()
