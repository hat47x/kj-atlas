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
    UserIdentityRow,
    UserRow,
)
from kj_atlas_api.session_context import CapabilitySnapshot
from kj_atlas_api.tenant_context import TenantContext, select_active_tenant_context


TIMESTAMP = "2026-08-06T00:00:00Z"


@dataclass
class StaticIdentityResolver:
    user_id: str = "user-1"

    def resolve(self, *, db: Session, request: Request) -> ResolvedIdentity:  # noqa: ARG002
        return ResolvedIdentity(
            user_id=self.user_id,
            reviewer_ref=f"user:{self.user_id}",
            owner_ref=f"user:{self.user_id}",
            auth_context=AuthContext(actor_ref=f"user:{self.user_id}", user_id=self.user_id),
        )


@dataclass
class MutableTenantResolver:
    tenant_id: str = "tenant-a"
    resolved_by: str = "verified_claim"

    def resolve(self, *, db: Session, user_id: str | None, claim: object = None) -> TenantContext:
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
    # G5 (W型 single-tenant 化): pre-provision the header-originated identity so
    # resolve_identity_context (single-tenant) resolves x-forwarded-user to user-1.
    db.add(UserIdentityRow(user_id="user-1", provider="oidc", external_uid="user-1", identity_provider_id=None, created_at=TIMESTAMP))
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
            # G5: single-tenant header-originated identity (resolve_identity_context
            # reads these; the SaaS resolver above is unused in single-tenant).
            client.headers.update({"x-forwarded-user": "user-1", "x-auth-provider": "oidc"})
            yield client, session_local, resolver
    finally:
        app.dependency_overrides.clear()
        app.state.saas_identity_context_resolver = None
        app.state.tenant_capability_resolver = None
        app.state.active_tenant_session_persister = None
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def _create(client: TestClient, journey_id: str, payload: object, headers: dict[str, str] | None = None) -> object:
    return client.post(
        f"/inquiry-bundles/{journey_id}",
        json=payload,
        headers={"If-None-Match": "*", **(headers or {})},
    )


def test_create_requires_if_none_match_and_get_returns_server_etag(tmp_path) -> None:
    bundle = {"version": 1, "journey": {"title": "private inquiry"}, "rounds": [1]}
    with _client(tmp_path) as fixture:
        client, session_local, _ = fixture
        missing = client.post("/inquiry-bundles/journey-1", json=bundle)
        created = _create(client, "journey-1", bundle)
        assert missing.status_code == 428
        assert created.status_code == 201
        assert created.headers["ETag"] == '"1"'

        fetched = client.get("/inquiry-bundles/journey-1")
        assert fetched.status_code == 200
        assert fetched.headers["ETag"] == '"1"'
        assert fetched.json() == bundle
        with session_local() as db:
            row = db.get(InquiryBundleRow, ("tenant-a", "journey-1"))
        assert row is not None
        assert row.revision == 1


def test_update_requires_single_canonical_if_match_and_increments_revision(tmp_path) -> None:
    with _client(tmp_path) as fixture:
        client, session_local, _ = fixture
        assert _create(client, "journey-1", {"version": 1}).status_code == 201

        # Missing / wildcard / comma list / non-integer If-Match all fail closed.
        assert client.post("/inquiry-bundles/journey-1", json={"v": 2}).status_code == 428
        assert (
            client.post(
                "/inquiry-bundles/journey-1",
                json={"v": 2},
                headers={"If-Match": "*"},
            ).status_code
            == 422
        )
        assert (
            client.post(
                "/inquiry-bundles/journey-1",
                json={"v": 2},
                headers={"If-Match": '"1", "2"'},
            ).status_code
            == 422
        )
        assert (
            client.post(
                "/inquiry-bundles/journey-1",
                json={"v": 2},
                headers={"If-Match": '"abc"'},
            ).status_code
            == 422
        )
        # If-Match and If-None-Match together are ambiguous.
        assert (
            client.post(
                "/inquiry-bundles/journey-1",
                json={"v": 2},
                headers={"If-Match": '"1"', "If-None-Match": "*"},
            ).status_code
            == 422
        )

        # Correct expected revision wins and bumps the revision.
        updated = client.post(
            "/inquiry-bundles/journey-1",
            json={"version": 2},
            headers={"If-Match": '"1"'},
        )
        assert updated.status_code == 204
        assert updated.headers["ETag"] == '"2"'
        with session_local() as db:
            row = db.get(InquiryBundleRow, ("tenant-a", "journey-1"))
        assert row is not None
        assert row.revision == 2
        assert json.loads(row.payload_json) == {"version": 2}


def test_stale_or_missing_update_fails_with_409_and_changes_nothing(tmp_path) -> None:
    with _client(tmp_path) as fixture:
        client, session_local, _ = fixture
        assert _create(client, "journey-1", {"version": 1}).status_code == 201

        stale = client.post(
            "/inquiry-bundles/journey-1",
            json={"version": 99},
            headers={"If-Match": '"1"'},
        )
        assert stale.status_code == 204
        # Second writer with the same old revision loses (AC-4 route view).
        loser = client.post(
            "/inquiry-bundles/journey-1",
            json={"version": 100},
            headers={"If-Match": '"1"'},
        )
        assert loser.status_code == 409
        assert loser.json()["detail"]["code"] == "inquiry_bundle_conflict"

        missing = client.post(
            "/inquiry-bundles/never-created",
            json={"version": 1},
            headers={"If-Match": '"1"'},
        )
        assert missing.status_code == 409

        with session_local() as db:
            row = db.get(InquiryBundleRow, ("tenant-a", "journey-1"))
        assert row is not None
        assert row.revision == 2
        assert json.loads(row.payload_json) == {"version": 99}


def test_create_when_row_exists_conflicts(tmp_path) -> None:
    with _client(tmp_path) as fixture:
        client, session_local, _ = fixture
        assert _create(client, "journey-1", {"version": 1}).status_code == 201
        again = client.post(
            "/inquiry-bundles/journey-1",
            json={"version": 2},
            headers={"If-None-Match": "*"},
        )
        assert again.status_code == 409
        with session_local() as db:
            row = db.get(InquiryBundleRow, ("tenant-a", "journey-1"))
        assert row is not None
        assert row.revision == 1
        assert json.loads(row.payload_json) == {"version": 1}


def test_delete_requires_if_match_and_writes_content_free_audit(tmp_path) -> None:
    with _client(tmp_path) as fixture:
        client, session_local, resolver = fixture
        assert _create(client, "shared", {"secret": "tenant-a-only"}).status_code == 201
        resolver.tenant_id = "tenant-b"
        assert _create(client, "shared", {"secret": "tenant-b-only"}).status_code == 201

        # Missing precondition is rejected before touching the row.
        assert client.delete("/inquiry-bundles/shared").status_code == 428
        # Stale revision leaves the row intact and writes no audit.
        stale = client.delete("/inquiry-bundles/shared", headers={"If-Match": '"9"'})
        assert stale.status_code == 409

        deleted = client.delete("/inquiry-bundles/shared", headers={"If-Match": '"1"'})
        assert deleted.status_code == 204
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


def test_missing_delete_with_if_match_conflicts_and_leaves_audit_empty(tmp_path) -> None:
    with _client(tmp_path) as fixture:
        client, session_local, _ = fixture
        assert _create(client, "retained", {"body": "keep"}).status_code == 201
        response = client.delete("/inquiry-bundles/missing", headers={"If-Match": '"1"'})
        with session_local() as db:
            retained = db.get(InquiryBundleRow, ("tenant-a", "retained"))
            events = db.scalars(select(InquiryBundleDeletionAuditEventRow)).all()

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "inquiry_bundle_conflict"
    assert retained is not None
    assert events == []


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

        response = client.post(
            "/inquiry-bundles/large-valid",
            json=payload,
            headers={"If-None-Match": "*"},
        )
        with session_local() as db:
            row = db.get(InquiryBundleRow, ("tenant-a", "large-valid"))

    assert response.status_code == 201
    assert row is not None
    assert json.loads(row.payload_json) == payload


def test_single_tenant_resolution_stores_bundle(tmp_path) -> None:
    # G5 (W型 single-tenant 化): a single-tenant adapter (no trusted SaaS
    # session) still stores the bundle under the resolved tenant.
    with _client(tmp_path) as fixture:
        client, _, resolver = fixture
        resolver.resolved_by = "single_tenant_adapter"
        response = client.post(
            "/inquiry-bundles/journey-1",
            json={"version": 1},
            headers={"If-None-Match": "*"},
        )

    assert response.status_code == 201


def _seed_second_user(session_local, *, tenant_id: str = "tenant-a") -> None:
    """SEC-INQUIRY-BOUND-01: a second provisioned identity, distinct from the
    fixture's default "user-1", sharing the same tenant membership so a
    denial can only be attributed to the new owner check -- not to tenant or
    membership scoping, which existing tests already cover separately."""
    with session_local() as db:
        db.add(
            UserRow(
                id="user-2",
                display_name=None,
                email=None,
                lifecycle_state="active",
                created_at=TIMESTAMP,
                updated_at=TIMESTAMP,
            )
        )
        db.add(
            UserIdentityRow(
                user_id="user-2",
                provider="oidc",
                external_uid="user-2",
                identity_provider_id=None,
                created_at=TIMESTAMP,
            )
        )
        db.add(
            TenantMembershipRow(
                tenant_id=tenant_id,
                user_id="user-2",
                lifecycle_state="active",
                created_at=TIMESTAMP,
                updated_at=TIMESTAMP,
            )
        )
        db.commit()


_AS_USER_2 = {"x-forwarded-user": "user-2", "x-auth-provider": "oidc"}


def test_create_sets_created_by_from_the_trusted_session(tmp_path) -> None:
    with _client(tmp_path) as fixture:
        client, session_local, _ = fixture
        assert _create(client, "journey-1", {"version": 1}).status_code == 201

        with session_local() as db:
            row = db.get(InquiryBundleRow, ("tenant-a", "journey-1"))
        assert row is not None
        assert row.created_by == "user-1"


def test_get_put_delete_deny_a_bundle_owned_by_another_user(tmp_path) -> None:
    with _client(tmp_path) as fixture:
        client, session_local, _ = fixture
        _seed_second_user(session_local)
        assert _create(client, "journey-1", {"version": 1}).status_code == 201

        get_denied = client.get("/inquiry-bundles/journey-1", headers=_AS_USER_2)
        assert get_denied.status_code == 403
        assert get_denied.json()["detail"]["code"] == "inquiry_bundle_not_owner"

        put_denied = client.post(
            "/inquiry-bundles/journey-1",
            json={"version": 2},
            headers={"If-Match": '"1"', **_AS_USER_2},
        )
        assert put_denied.status_code == 403
        assert put_denied.json()["detail"]["code"] == "inquiry_bundle_not_owner"

        delete_denied = client.delete(
            "/inquiry-bundles/journey-1", headers={"If-Match": '"1"', **_AS_USER_2}
        )
        assert delete_denied.status_code == 403
        assert delete_denied.json()["detail"]["code"] == "inquiry_bundle_not_owner"

        # Nothing was mutated by any of the three denied attempts.
        with session_local() as db:
            row = db.get(InquiryBundleRow, ("tenant-a", "journey-1"))
        assert row is not None
        assert row.revision == 1
        assert json.loads(row.payload_json) == {"version": 1}

        # The actual owner is unaffected.
        owner_get = client.get("/inquiry-bundles/journey-1")
        assert owner_get.status_code == 200
        assert owner_get.json() == {"version": 1}


def test_pre_migration_bundle_with_no_created_by_keeps_tenant_wide_access(tmp_path) -> None:
    """created_by is only enforced when it is actually set (SEC-INQUIRY-BOUND-01
    decision: enforce for newly created bundles only, do not retroactively
    lock existing bundles that predate this column)."""
    with _client(tmp_path) as fixture:
        client, session_local, _ = fixture
        _seed_second_user(session_local)
        assert _create(client, "legacy-journey", {"version": 1}).status_code == 201
        with session_local() as db:
            row = db.get(InquiryBundleRow, ("tenant-a", "legacy-journey"))
            assert row is not None
            row.created_by = None
            db.commit()

        get_as_other_user = client.get("/inquiry-bundles/legacy-journey", headers=_AS_USER_2)
        assert get_as_other_user.status_code == 200

        put_as_other_user = client.post(
            "/inquiry-bundles/legacy-journey",
            json={"version": 2},
            headers={"If-Match": '"1"', **_AS_USER_2},
        )
        assert put_as_other_user.status_code == 204

        delete_as_other_user = client.delete(
            "/inquiry-bundles/legacy-journey", headers={"If-Match": '"2"', **_AS_USER_2}
        )
        assert delete_as_other_user.status_code == 204


def test_etag_known_in_one_tenant_cannot_touch_another_tenants_bundle(tmp_path) -> None:
    # AC-7: the same journey id and revision exist in tenant A and B. Tenant
    # B's writes/deletes always carry tenant_id=tenant-b in the CAS predicate,
    # so even a known revision never reaches tenant A's row.
    with _client(tmp_path) as fixture:
        client, session_local, resolver = fixture
        assert _create(client, "same-id", {"owner": "a"}).status_code == 201
        a_etag = client.get("/inquiry-bundles/same-id").headers["ETag"]  # '"1"'
        resolver.tenant_id = "tenant-b"
        assert _create(client, "same-id", {"owner": "b"}).status_code == 201

        # tenant B updates and deletes its own row using the same revision
        # value it observed in tenant A — tenant A's row is never touched.
        assert (
            client.post(
                "/inquiry-bundles/same-id",
                json={"owner": "b2"},
                headers={"If-Match": a_etag},
            ).status_code
            == 204
        )
        assert (
            client.delete("/inquiry-bundles/same-id", headers={"If-Match": '"2"'}).status_code
            == 204
        )

        resolver.tenant_id = "tenant-a"
        a_get = client.get("/inquiry-bundles/same-id")
        assert a_get.status_code == 200
        assert a_get.json() == {"owner": "a"}
        assert a_get.headers["ETag"] == '"1"'
        with session_local() as db:
            a_row = db.get(InquiryBundleRow, ("tenant-a", "same-id"))
            b_row = db.get(InquiryBundleRow, ("tenant-b", "same-id"))
        assert a_row is not None
        assert a_row.revision == 1
        assert b_row is None
