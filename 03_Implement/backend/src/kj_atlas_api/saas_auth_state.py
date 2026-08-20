"""Shared, fail-closed persistence for horizontally scaled SaaS authentication."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from kj_atlas_api.models import SaasAuthSessionRow, SaasTenantSessionRow


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value)


class DatabaseSaasAuthStateStore:
    """Use independent short transactions so auth state is immediately shared."""

    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory

    def current_or_create_session_version(
        self, *, principal_id: str, new_version: str
    ) -> str:
        with self._session_factory() as db:
            current = db.scalar(
                select(SaasTenantSessionRow.session_version).where(
                    SaasTenantSessionRow.principal_id == principal_id
                )
            )
            if current is not None:
                return current
            db.add(
                SaasTenantSessionRow(
                    principal_id=principal_id,
                    session_version=new_version,
                    updated_at=_now_iso(),
                )
            )
            try:
                db.commit()
                return new_version
            except IntegrityError:
                db.rollback()
                winner = db.scalar(
                    select(SaasTenantSessionRow.session_version).where(
                        SaasTenantSessionRow.principal_id == principal_id
                    )
                )
                if winner is None:
                    raise
                return winner

    def rotate_session_version(
        self, *, principal_id: str, expected_version: str, new_version: str
    ) -> bool:
        with self._session_factory() as db:
            result = db.execute(
                update(SaasTenantSessionRow)
                .where(
                    SaasTenantSessionRow.principal_id == principal_id,
                    SaasTenantSessionRow.session_version == expected_version,
                )
                .values(session_version=new_version, updated_at=_now_iso())
            )
            if result.rowcount != 1:
                db.rollback()
                return False
            db.commit()
            return True

    def clear_session_version(self, *, session_version: str) -> None:
        with self._session_factory() as db:
            db.execute(
                delete(SaasTenantSessionRow).where(
                    SaasTenantSessionRow.session_version == session_version
                )
            )
            db.commit()

    def preflight(self) -> None:
        """Fail startup when the shared tenant-session table is inaccessible."""
        with self._session_factory() as db:
            db.execute(select(SaasTenantSessionRow.principal_id).limit(1))


# ADR-0074 decision 3 / 回答案2: fixed, non-configurable lifetimes -- no
# settings field exists for either, matching the ADR's proposed literal 12h
# absolute / 60min idle values rather than inventing tunables AC-1 doesn't
# need yet.
_ABSOLUTE_SESSION_LIFETIME = timedelta(hours=12)
_IDLE_TIMEOUT = timedelta(minutes=60)


@dataclass(frozen=True, slots=True)
class ResolvedAuthSession:
    """The subset of a live SaasAuthSessionRow the identity resolver needs to
    reconstruct a VerifiedTenantClaim (ADR-0074 decision 3)."""

    principal_id: str
    issuer: str
    subject: str
    active_tenant_id: str | None


class DatabaseSaasAuthSessionStore:
    """ADR-0074 decision 3: server-owned auth sessions, keyed by
    session_key_hash (a keyed hash of the opaque cookie value -- the raw
    value is never persisted, see auth_session_hash.py).
    """

    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory

    def create_auth_session(
        self,
        *,
        session_key_hash: str,
        principal_id: str,
        issuer: str,
        subject: str,
        active_tenant_id: str | None,
        tenant_session_version: str,
    ) -> None:
        now = datetime.now(timezone.utc)
        with self._session_factory() as db:
            db.add(
                SaasAuthSessionRow(
                    session_key_hash=session_key_hash,
                    principal_id=principal_id,
                    issuer=issuer,
                    subject=subject,
                    active_tenant_id=active_tenant_id,
                    tenant_session_version=tenant_session_version,
                    created_at=now.isoformat(),
                    last_used_at=now.isoformat(),
                    absolute_expires_at=(now + _ABSOLUTE_SESSION_LIFETIME).isoformat(),
                    revoked_at=None,
                )
            )
            db.commit()

    def resolve_auth_session(self, *, session_key_hash: str) -> ResolvedAuthSession | None:
        """Look up a session, rejecting revoked/absolutely-expired/idle-expired
        rows, and refresh last_used_at on a hit (sliding idle window)."""
        now = datetime.now(timezone.utc)
        with self._session_factory() as db:
            row = db.get(SaasAuthSessionRow, session_key_hash)
            if row is None or row.revoked_at is not None:
                return None
            if _parse_iso(row.absolute_expires_at) <= now:
                return None
            if _parse_iso(row.last_used_at) + _IDLE_TIMEOUT <= now:
                return None
            resolved = ResolvedAuthSession(
                principal_id=row.principal_id,
                issuer=row.issuer,
                subject=row.subject,
                active_tenant_id=row.active_tenant_id,
            )
            row.last_used_at = now.isoformat()
            db.commit()
            return resolved

    def revoke_auth_session(self, *, session_key_hash: str) -> None:
        with self._session_factory() as db:
            db.execute(
                update(SaasAuthSessionRow)
                .where(SaasAuthSessionRow.session_key_hash == session_key_hash)
                .values(revoked_at=_now_iso())
            )
            db.commit()

    def preflight(self) -> None:
        """Fail startup when the auth-session table is inaccessible."""
        with self._session_factory() as db:
            db.execute(select(SaasAuthSessionRow.session_key_hash).limit(1))
