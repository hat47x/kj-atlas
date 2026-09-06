from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine, update
from sqlalchemy.orm import Session, sessionmaker

from kj_atlas_api.guest_admission_models import GuestPrincipalRow
from kj_atlas_api.guest_auth_session_models import GuestAuthSessionRow
from kj_atlas_api.guest_auth_state import DatabaseGuestAuthSessionStore, GuestAuthSessionError
from kj_atlas_api.models import Base, TenantRow

TIMESTAMP = "2026-09-06T00:00:00+00:00"
SESSION_HASH = "a" * 64
ISSUER = "https://guest-idp.invalid"
SUBJECT = "guest-subject-1"


@pytest.fixture
def store_and_factory(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path}/guest-auth.db")
    factory = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)
    Base.metadata.create_all(engine)
    with factory() as db:
        db.add(
            TenantRow(
                id="tenant-a",
                display_name="Tenant A",
                lifecycle_state="active",
                created_at=TIMESTAMP,
                updated_at=TIMESTAMP,
            )
        )
        db.add(
            GuestPrincipalRow(
                tenant_id="tenant-a",
                guest_principal_id="guest-1",
                invited_email="guest@example.invalid",
                status="active",
                verification_method="personal_account",
                verified_issuer=ISSUER,
                verified_subject=SUBJECT,
                created_by="owner-1",
                created_at=TIMESTAMP,
                expires_at="2026-09-07T00:00:00+00:00",
                redeemed_at=TIMESTAMP,
                revoked_at=None,
            )
        )
        db.commit()
    yield DatabaseGuestAuthSessionStore(factory), factory
    engine.dispose()


def _create(store: DatabaseGuestAuthSessionStore, *, session_hash: str = SESSION_HASH) -> None:
    store.create_guest_auth_session(
        session_key_hash=session_hash,
        tenant_id="tenant-a",
        guest_principal_id="guest-1",
        issuer=ISSUER,
        subject=SUBJECT,
    )


def test_create_and_resolve_live_guest_session(store_and_factory) -> None:
    store, _ = store_and_factory
    _create(store)

    resolved = store.resolve_guest_auth_session(session_key_hash=SESSION_HASH)

    assert resolved is not None
    assert resolved.tenant_id == "tenant-a"
    assert resolved.guest_principal_id == "guest-1"
    assert resolved.issuer == ISSUER
    assert resolved.subject == SUBJECT


def test_session_creation_requires_exact_verified_identity(store_and_factory) -> None:
    store, _ = store_and_factory

    with pytest.raises(GuestAuthSessionError):
        store.create_guest_auth_session(
            session_key_hash=SESSION_HASH,
            tenant_id="tenant-a",
            guest_principal_id="guest-1",
            issuer=ISSUER,
            subject="wrong-subject",
        )


def test_revoked_principal_invalidates_existing_session_on_next_resolution(store_and_factory) -> None:
    store, factory = store_and_factory
    _create(store)
    with factory() as db:
        principal = db.get(GuestPrincipalRow, ("tenant-a", "guest-1"))
        assert principal is not None
        principal.status = "revoked"
        principal.revoked_at = datetime.now(timezone.utc).isoformat()
        db.commit()

    assert store.resolve_guest_auth_session(session_key_hash=SESSION_HASH) is None


def test_expired_or_idle_session_fails_closed(store_and_factory) -> None:
    store, factory = store_and_factory
    _create(store)
    stale = datetime.now(timezone.utc) - timedelta(hours=2)
    with factory() as db:
        db.execute(
            update(GuestAuthSessionRow)
            .where(GuestAuthSessionRow.session_key_hash == SESSION_HASH)
            .values(last_used_at=stale.isoformat())
        )
        db.commit()

    assert store.resolve_guest_auth_session(session_key_hash=SESSION_HASH) is None


def test_explicit_session_revoke_fails_closed(store_and_factory) -> None:
    store, _ = store_and_factory
    _create(store)

    store.revoke_guest_auth_session(session_key_hash=SESSION_HASH)

    assert store.resolve_guest_auth_session(session_key_hash=SESSION_HASH) is None
