"""Shared, fail-closed persistence for horizontally scaled SaaS authentication."""

from __future__ import annotations

import hashlib
from threading import Lock
from collections.abc import Callable
from datetime import datetime, timezone

from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from kj_atlas_api.models import JwtReplayTokenRow, SaasTenantSessionRow


class ReplayDetectedError(Exception):
    """The same provider-scoped JWT ID was already consumed."""


class InMemoryReplayStore:
    """Resolver-local test adapter; never installed by the SaaS runtime."""

    def __init__(self) -> None:
        self._seen: set[str] = set()
        self._lock = Lock()

    def record_jti(self, *, provider_id: str, jti: str, expires_at: datetime) -> None:
        key = f"{provider_id}\0{jti}"
        with self._lock:
            if key in self._seen:
                raise ReplayDetectedError
            self._seen.add(key)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


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

    def record_jti(self, *, provider_id: str, jti: str, expires_at: datetime) -> None:
        digest = hashlib.sha256(f"{provider_id}\0{jti}".encode()).hexdigest()
        now = _now_iso()
        with self._session_factory() as db:
            # Permit reuse only after the prior token's verified expiry window.
            db.execute(
                delete(JwtReplayTokenRow).where(
                    JwtReplayTokenRow.token_digest == digest,
                    JwtReplayTokenRow.expires_at <= now,
                )
            )
            db.add(
                JwtReplayTokenRow(
                    token_digest=digest,
                    expires_at=expires_at.astimezone(timezone.utc).isoformat(),
                    recorded_at=now,
                )
            )
            try:
                db.commit()
            except IntegrityError:
                db.rollback()
                raise ReplayDetectedError from None

    def preflight(self) -> None:
        """Fail startup when the shared auth tables are absent or inaccessible."""
        with self._session_factory() as db:
            db.execute(select(SaasTenantSessionRow.principal_id).limit(1))
            db.execute(select(JwtReplayTokenRow.token_digest).limit(1))
