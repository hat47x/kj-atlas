"""SAAS-TENANT-SESSION-BINDING-01 AC-2/AC-3: the session-keyed branches of
resolve_active_tenant_session_version()/persist_active_tenant_selection()
(auth_session_key_hash present) read and CAS-write SaasAuthSessionRow
directly, bypassing the principal-keyed persister entirely (AC-6: no
fallback to it on any failure).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from kj_atlas_api.active_tenant_session import (
    persist_active_tenant_selection,
    resolve_active_tenant_session_version,
)
from kj_atlas_api.models import Base, SaasAuthSessionRow, TenantRow
from kj_atlas_api.saas_auth_state import DatabaseSaasAuthSessionStore
from kj_atlas_api.tenant_context import TenantContext

_ISSUER = "https://idp.example.test"


def _tenant_ctx(tenant_id: str) -> TenantContext:
    return TenantContext(
        tenant_id=tenant_id,
        membership_id=f"membership-{tenant_id}",
        resolved_by="verified_claim",
    )


@dataclass
class _FakeState:
    saas_auth_session_store: object | None = None
    active_tenant_session_persister: object | None = None


@dataclass
class _FakeApp:
    state: _FakeState


@dataclass
class _FakeRequest:
    app: _FakeApp


def _request(store: object | None) -> _FakeRequest:
    return _FakeRequest(app=_FakeApp(state=_FakeState(saas_auth_session_store=store)))


def _store(tmp_path, name: str = "keyed.db"):
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


def _create_session(
    store: DatabaseSaasAuthSessionStore,
    session_key_hash: str,
    *,
    active_tenant_id: str,
    version: str = "version-1",
) -> None:
    store.create_auth_session(
        session_key_hash=session_key_hash,
        principal_id="principal-1",
        issuer=_ISSUER,
        subject="subject-1",
        active_tenant_id=active_tenant_id,
        tenant_session_version=version,
    )


def _stored_row(factory, session_key_hash: str) -> SaasAuthSessionRow:
    with factory() as db:
        row = db.get(SaasAuthSessionRow, session_key_hash)
        assert row is not None
        return row


class TestResolveSessionKeyedVersion:
    def test_reads_version_from_the_auth_session_row(self, tmp_path) -> None:
        store, factory = _store(tmp_path)
        _seed_tenant(factory, "tenant-a")
        _create_session(store, "hash-1", active_tenant_id="tenant-a", version="version-7")

        version = resolve_active_tenant_session_version(
            request=_request(store),
            principal_id="principal-1",
            active_tenant=_tenant_ctx("tenant-a"),
            auth_session_key_hash="hash-1",
        )

        assert version == "version-7"

    def test_fails_closed_when_the_store_is_unwired(self, tmp_path) -> None:
        with pytest.raises(HTTPException) as exc:
            resolve_active_tenant_session_version(
                request=_request(None),
                principal_id="principal-1",
                active_tenant=_tenant_ctx("tenant-a"),
                auth_session_key_hash="hash-1",
            )

        assert exc.value.status_code == 503
        assert exc.value.detail["code"] == "session_context_unavailable"

    def test_fails_closed_when_the_session_is_unknown_and_does_not_use_principal_id(
        self, tmp_path
    ) -> None:
        """AC-6: an unresolvable session must not fall back to principal-keyed
        state -- even though principal_id is available, no version is
        conjured from it."""
        store, _ = _store(tmp_path)

        with pytest.raises(HTTPException) as exc:
            resolve_active_tenant_session_version(
                request=_request(store),
                principal_id="principal-1",
                active_tenant=_tenant_ctx("tenant-a"),
                auth_session_key_hash="never-created",
            )

        assert exc.value.status_code == 503
        assert exc.value.detail["code"] == "session_context_unavailable"


class TestPersistSessionKeyedSelection:
    def test_rotates_the_auth_session_row_and_returns_a_fresh_version(self, tmp_path) -> None:
        store, factory = _store(tmp_path)
        _seed_tenant(factory, "tenant-a")
        _seed_tenant(factory, "tenant-b")
        _create_session(store, "hash-1", active_tenant_id="tenant-a", version="version-1")

        new_version = persist_active_tenant_selection(
            request=_request(store),
            response=SimpleNamespace(),
            principal_id="principal-1",
            previous_tenant=_tenant_ctx("tenant-a"),
            selected_tenant=_tenant_ctx("tenant-b"),
            expected_tenant_session_version="version-1",
            auth_session_key_hash="hash-1",
        )

        assert new_version != "version-1"
        row = _stored_row(factory, "hash-1")
        assert row.active_tenant_id == "tenant-b"
        assert row.tenant_session_version == new_version

    def test_stale_expected_version_is_rejected_without_mutating_the_row(self, tmp_path) -> None:
        store, factory = _store(tmp_path)
        _seed_tenant(factory, "tenant-a")
        _seed_tenant(factory, "tenant-b")
        _create_session(store, "hash-1", active_tenant_id="tenant-a", version="version-1")

        with pytest.raises(HTTPException) as exc:
            persist_active_tenant_selection(
                request=_request(store),
                response=SimpleNamespace(),
                principal_id="principal-1",
                previous_tenant=_tenant_ctx("tenant-a"),
                selected_tenant=_tenant_ctx("tenant-b"),
                expected_tenant_session_version="stale-version",
                auth_session_key_hash="hash-1",
            )

        assert exc.value.status_code == 409
        assert exc.value.detail["code"] == "tenant_session_changed"
        row = _stored_row(factory, "hash-1")
        assert row.active_tenant_id == "tenant-a"
        assert row.tenant_session_version == "version-1"

    def test_fails_closed_when_the_store_is_unwired(self) -> None:
        with pytest.raises(HTTPException) as exc:
            persist_active_tenant_selection(
                request=_request(None),
                response=SimpleNamespace(),
                principal_id="principal-1",
                previous_tenant=_tenant_ctx("tenant-a"),
                selected_tenant=_tenant_ctx("tenant-b"),
                expected_tenant_session_version="version-1",
                auth_session_key_hash="hash-1",
            )

        assert exc.value.status_code == 503
        assert exc.value.detail["code"] == "active_tenant_update_unavailable"

    def test_does_not_set_any_cookie_on_the_response(self, tmp_path) -> None:
        """The presented Kj-Atlas-Auth-Session cookie is already the binding;
        a session-keyed switch must not also mint a version cookie."""
        store, factory = _store(tmp_path)
        _seed_tenant(factory, "tenant-a")
        _seed_tenant(factory, "tenant-b")
        _create_session(store, "hash-1", active_tenant_id="tenant-a", version="version-1")
        response = SimpleNamespace()

        persist_active_tenant_selection(
            request=_request(store),
            response=response,
            principal_id="principal-1",
            previous_tenant=_tenant_ctx("tenant-a"),
            selected_tenant=_tenant_ctx("tenant-b"),
            expected_tenant_session_version="version-1",
            auth_session_key_hash="hash-1",
        )

        assert not hasattr(response, "headers")


class TestPrincipalKeyedDispatchIsUnaffected:
    """Locks in the branch condition itself: omitting auth_session_key_hash
    must still route to the existing principal-keyed persister, unchanged."""

    def test_resolve_without_a_session_hash_uses_the_persister(self) -> None:
        from kj_atlas_api.active_tenant_session import InMemoryActiveTenantSessionPersister

        persister = InMemoryActiveTenantSessionPersister()
        request = _FakeRequest(
            app=_FakeApp(state=_FakeState(active_tenant_session_persister=persister))
        )

        version = resolve_active_tenant_session_version(
            request=request,
            principal_id="principal-1",
            active_tenant=_tenant_ctx("tenant-a"),
        )

        assert version == persister._sessions["principal-1"]
