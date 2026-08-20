"""SAAS-TENANT-SESSION-BINDING-01 AC-1: the BFF auth-session store and its
keyed cookie hashing shipped without tests. These fix the fail-closed
lifetime/revocation contract (ADR-0074 decisions 2/3) in place.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine, select, update
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, sessionmaker

from kj_atlas_api.auth_session_hash import derive_session_key_hash
from kj_atlas_api.models import Base, SaasAuthSessionRow, TenantRow
from kj_atlas_api.saas_auth_state import DatabaseSaasAuthSessionStore

_KEY = b"hash-key-for-tests-0123456789ab"
_ISSUER = "https://idp.example.test"


def _store(tmp_path, name: str = "auth-sessions.db"):
    engine = create_engine(
        f"sqlite:///{tmp_path / name}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)
    return DatabaseSaasAuthSessionStore(factory), factory


def _seed_tenant(factory, tenant_id: str) -> None:
    now = datetime.now(timezone.utc).isoformat()
    with factory() as db:
        db.add(
            TenantRow(
                id=tenant_id,
                display_name=tenant_id,
                lifecycle_state="active",
                created_at=now,
                updated_at=now,
            )
        )
        db.commit()


def _create(
    store: DatabaseSaasAuthSessionStore,
    session_key_hash: str,
    *,
    principal_id: str = "principal-1",
    active_tenant_id: str | None = None,
) -> None:
    store.create_auth_session(
        session_key_hash=session_key_hash,
        principal_id=principal_id,
        issuer=_ISSUER,
        subject="subject-1",
        active_tenant_id=active_tenant_id,
        tenant_session_version="version-1",
    )


def _backdate(
    factory,
    session_key_hash: str,
    *,
    last_used: datetime | None = None,
    absolute_expires: datetime | None = None,
) -> None:
    values: dict[str, str] = {}
    if last_used is not None:
        values["last_used_at"] = last_used.isoformat()
    if absolute_expires is not None:
        values["absolute_expires_at"] = absolute_expires.isoformat()
    with factory() as db:
        db.execute(
            update(SaasAuthSessionRow)
            .where(SaasAuthSessionRow.session_key_hash == session_key_hash)
            .values(**values)
        )
        db.commit()


def _stored_last_used(factory, session_key_hash: str) -> datetime:
    with factory() as db:
        raw = db.execute(
            select(SaasAuthSessionRow.last_used_at).where(
                SaasAuthSessionRow.session_key_hash == session_key_hash
            )
        ).scalar_one()
    return datetime.fromisoformat(raw)


def test_session_key_hash_is_deterministic_key_dependent_and_hides_the_raw_value() -> None:
    raw = "opaque-session-id-abcdefghijklmnop"

    assert derive_session_key_hash(raw, key=_KEY) == derive_session_key_hash(raw, key=_KEY)
    assert derive_session_key_hash(raw, key=_KEY) != derive_session_key_hash(raw, key=b"other-key")
    assert derive_session_key_hash(raw, key=_KEY) != derive_session_key_hash("other-raw", key=_KEY)
    # ADR-0074 decision 2: the raw cookie value must never be recoverable from
    # what is persisted.
    assert raw not in derive_session_key_hash(raw, key=_KEY)


def test_created_session_resolves_with_the_stored_identity_and_active_tenant(tmp_path) -> None:
    store, factory = _store(tmp_path)
    _seed_tenant(factory, "tenant-a")
    key_hash = derive_session_key_hash("session-live", key=_KEY)

    _create(store, key_hash, active_tenant_id="tenant-a")
    resolved = store.resolve_auth_session(session_key_hash=key_hash)

    assert resolved is not None
    assert resolved.principal_id == "principal-1"
    assert resolved.issuer == _ISSUER
    assert resolved.subject == "subject-1"
    assert resolved.active_tenant_id == "tenant-a"


def test_unknown_session_key_hash_resolves_to_none(tmp_path) -> None:
    store, _ = _store(tmp_path)

    assert store.resolve_auth_session(session_key_hash="never-created") is None


def test_revoked_session_resolves_to_none(tmp_path) -> None:
    store, _ = _store(tmp_path)
    key_hash = derive_session_key_hash("session-revoked", key=_KEY)
    _create(store, key_hash)
    assert store.resolve_auth_session(session_key_hash=key_hash) is not None

    store.revoke_auth_session(session_key_hash=key_hash)

    assert store.resolve_auth_session(session_key_hash=key_hash) is None


def test_absolutely_expired_session_resolves_to_none(tmp_path) -> None:
    store, factory = _store(tmp_path)
    key_hash = derive_session_key_hash("session-absolute", key=_KEY)
    _create(store, key_hash)
    now = datetime.now(timezone.utc)

    # Past the 12h absolute lifetime while still inside the idle window.
    _backdate(factory, key_hash, absolute_expires=now - timedelta(seconds=1), last_used=now)

    assert store.resolve_auth_session(session_key_hash=key_hash) is None


def test_idle_expired_session_resolves_to_none(tmp_path) -> None:
    store, factory = _store(tmp_path)
    key_hash = derive_session_key_hash("session-idle", key=_KEY)
    _create(store, key_hash)

    # Past the 60min idle timeout while the absolute expiry is still in future.
    _backdate(factory, key_hash, last_used=datetime.now(timezone.utc) - timedelta(minutes=61))

    assert store.resolve_auth_session(session_key_hash=key_hash) is None


def test_resolving_slides_the_idle_window(tmp_path) -> None:
    store, factory = _store(tmp_path)
    key_hash = derive_session_key_hash("session-sliding", key=_KEY)
    _create(store, key_hash)
    stale = datetime.now(timezone.utc) - timedelta(minutes=59)
    _backdate(factory, key_hash, last_used=stale)

    assert store.resolve_auth_session(session_key_hash=key_hash) is not None

    # The hit refreshed last_used_at, so the session survives another idle window.
    assert _stored_last_used(factory, key_hash) > stale
    assert store.resolve_auth_session(session_key_hash=key_hash) is not None


def test_revoking_one_login_session_does_not_affect_another_of_the_same_principal(
    tmp_path,
) -> None:
    """ADR-0074 decision 3: row identity is the login session, not the principal."""
    store, _ = _store(tmp_path)
    browser_a = derive_session_key_hash("session-browser-a", key=_KEY)
    browser_b = derive_session_key_hash("session-browser-b", key=_KEY)
    _create(store, browser_a, principal_id="principal-shared")
    _create(store, browser_b, principal_id="principal-shared")

    store.revoke_auth_session(session_key_hash=browser_a)

    assert store.resolve_auth_session(session_key_hash=browser_a) is None
    assert store.resolve_auth_session(session_key_hash=browser_b) is not None


def test_preflight_fails_when_the_auth_session_table_is_missing(tmp_path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'unmigrated.db'}")
    factory = sessionmaker(bind=engine, class_=Session)

    with pytest.raises(OperationalError):
        DatabaseSaasAuthSessionStore(factory).preflight()
