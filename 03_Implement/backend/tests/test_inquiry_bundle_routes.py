from __future__ import annotations

import json
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass

from fastapi import Request
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from kj_atlas_api.access_control import AuthContext
from kj_atlas_api.auth_context import ResolvedIdentity
from kj_atlas_api.db import get_db
from kj_atlas_api.main import app
from kj_atlas_api.models import (
    Base,
    InquiryBundleDeletionAuditEventRow,
    InquiryBundleRow,
    TenantMembershipRow,
    TenantRow,
    UserRow,
)
from kj_atlas_api.session_context import CapabilitySnapshot
from kj_atlas_api.tenant_context import TenantContext, select_active_tenant_context


TIMESTAMP = "2026-08-06T00:00:00Z"


@dataclass
class StaticIdentityResolver:
    def resolve(self, *, db: Session, request: Request) -> ResolvedIdentity:  # noqa: ARG002
        return ResolvedIdentity(
            user_id="user-1",
            reviewer_ref="user:user-1",
            owner_ref="user:user-1",
            auth_context=AuthContext(actor_ref="user:user-1", user_id="user-1"),
        )


@dataclass
class MutableTenantResolver:
    tenant_id: str = "tenant-a"
    resolved_by: str = "verified_claim"

    def resolve(self, *, db: Session, user_id: str | None, claim: object = None) -> TenantContext:
        assert user_id == "user-1"
        if self.resolved_by in {"verified_claim", "trusted_host_mapping"}:
            return select_active_tenant_context(
                db=db,
                user_id=user_id,
                tenant_id=self.tenant_id,
                resolved_by=self.resolved_by,  # type: ignore[arg-type]
            )
        return TenantContext(
            tenant_id=self.tenant_id,
            membership_id=None,
            resolved_by="single_tenant_adapter",
        )


class StaticCapabilityResolver:
    def resolve(self, **_: object) -> CapabilitySnapshot:
        return CapabilitySnapshot(effective_capabilities=(), capability_version="capability-v1")


class StaticTenantSessionPersister:
    def current_version(self, **_: object) -> str:
        return "session-v1"


def _seed(db: Session) -> None:
    db.add(UserRow(id="user-1", display_name=None, email=None, lifecycle_state="active", created_at=TIMESTAMP, updated_at=TIMESTAMP))
    for tenant_id in ("tenant-a", "tenant-b"):
        db.add(TenantRow(id=tenant_id, display_name=tenant_id, lifecycle_state="active", created_at=TIMESTAMP, updated_at=TIMESTAMP))
        db.add(TenantMembershipRow(tenant_id=tenant_id, user_id="user-1", lifecycle_state="active", created_at=TIMESTAMP, updated_at=TIMESTAMP))
    db.commit()


@contextmanager
def _client(tmp_path) -> Iterator[tuple[TestClient, sessionmaker[Session], MutableTenantResolver]]:
    engine = create_engine(f"sqlite:///{tmp_path / 'inquiry-bundles.sqlite3'}")
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)
    with session_local() as db:
        _seed(db)

    def _get_test_db():
        db = session_local()
        try:
            yield db
        finally:
            db.close()

    resolver = MutableTenantResolver()
    app.dependency_overrides[get_db] = _get_test_db
    try:
        with TestClient(app) as client:
            client.app.state.saas_identity_context_resolver = StaticIdentityResolver()
            client.app.state.tenant_context_resolver = resolver
            client.app.state.tenant_capability_resolver = StaticCapabilityResolver()
            client.app.state.active_tenant_session_persister = StaticTenantSessionPersister()
            yield client, session_local, resolver
    finally:
        app.dependency_overrides.clear()
        app.state.saas_identity_context_resolver = None
        app.state.tenant_capability_resolver = None
        app.state.active_tenant_session_persister = None
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_save_get_and_overwrite_keep_payload_opaque(tmp_path) -> None:
    bundle = {"version": 1, "journey": {"title": "private inquiry"}, "rounds": [1]}
    with _client(tmp_path) as fixture:
        client, session_local, _ = fixture
        assert client.post("/inquiry-bundles/journey-1", json=bundle).status_code == 204
        assert client.get("/inquiry-bundles/journey-1").json() == bundle
        replacement = {"version": 1, "foreignFutureField": {"keep": True}}
        assert client.post("/inquiry-bundles/journey-1", json=replacement).status_code == 204
        with session_local() as db:
            rows = db.scalars(select(InquiryBundleRow)).all()

    assert len(rows) == 1
    assert rows[0].journey_id == "journey-1"
    assert "foreignFutureField" in rows[0].payload_json


def test_get_and_delete_are_tenant_scoped_and_delete_writes_content_free_audit(tmp_path) -> None:
    with _client(tmp_path) as fixture:
        client, session_local, resolver = fixture
        assert client.post("/inquiry-bundles/shared", json={"secret": "tenant-a-only"}).status_code == 204
        resolver.tenant_id = "tenant-b"
        assert client.post("/inquiry-bundles/shared", json={"secret": "tenant-b-only"}).status_code == 204
        assert client.delete("/inquiry-bundles/shared").status_code == 204
        assert client.get("/inquiry-bundles/shared").status_code == 404
        resolver.tenant_id = "tenant-a"
        response = client.get("/inquiry-bundles/shared")
        with session_local() as db:
            a_row = db.get(InquiryBundleRow, ("tenant-a", "shared"))
            b_row = db.get(InquiryBundleRow, ("tenant-b", "shared"))
            events = db.scalars(select(InquiryBundleDeletionAuditEventRow)).all()

    assert response.status_code == 200
    assert response.json() == {"secret": "tenant-a-only"}
    assert a_row is not None
    assert b_row is None
    assert len(events) == 1
    assert events[0].tenant_id == "tenant-b"
    assert events[0].journey_id == "shared"
    assert events[0].principal_id == "user-1"
    assert events[0].action == "inquiry_bundle.delete"
    assert events[0].outcome == "deleted"
    assert "secret" not in str(events[0].__dict__)
    assert "tenant-b-only" not in str(events[0].__dict__)


def test_missing_journey_id_and_payload_over_absolute_limit_are_rejected(tmp_path) -> None:
    with _client(tmp_path) as fixture:
        client, session_local, _ = fixture
        empty = client.post("/inquiry-bundles/%20", json={"version": 1})
        oversized = client.post(
            "/inquiry-bundles/too-big",
            json={"data": "x" * (20 * 1024 * 1024)},
        )
        with session_local() as db:
            rows = db.scalars(select(InquiryBundleRow)).all()

    assert empty.status_code == 422
    assert empty.json()["detail"]["code"] == "invalid_journey_id"
    assert oversized.status_code == 413
    assert oversized.json()["detail"]["code"] == "inquiry_bundle_too_large"
    assert rows == []


def test_payload_above_warning_boundary_but_below_absolute_limit_is_stored(tmp_path) -> None:
    with _client(tmp_path) as fixture:
        client, session_local, _ = fixture
        payload = {"data": "x" * (5 * 1024 * 1024)}

        response = client.post("/inquiry-bundles/large-valid", json=payload)
        with session_local() as db:
            row = db.get(InquiryBundleRow, ("tenant-a", "large-valid"))

    assert response.status_code == 204
    assert row is not None
    assert json.loads(row.payload_json) == payload


def test_routes_fail_closed_without_trusted_server_resolved_tenant(tmp_path) -> None:
    with _client(tmp_path) as fixture:
        client, _, resolver = fixture
        resolver.resolved_by = "single_tenant_adapter"
        response = client.post("/inquiry-bundles/journey-1", json={"version": 1})

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "tenant_context_untrusted"


def test_missing_delete_does_not_create_audit_or_mutate_existing_bundles(tmp_path) -> None:
    with _client(tmp_path) as fixture:
        client, session_local, _ = fixture
        assert client.post("/inquiry-bundles/retained", json={"body": "keep"}).status_code == 204
        response = client.delete("/inquiry-bundles/missing")
        with session_local() as db:
            retained = db.get(InquiryBundleRow, ("tenant-a", "retained"))
            events = db.scalars(select(InquiryBundleDeletionAuditEventRow)).all()

    assert response.status_code == 404
    assert response.json()["detail"] == "Inquiry bundle not found"
    assert retained is not None
    assert events == []
