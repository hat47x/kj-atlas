from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass

import pytest
from fastapi import Request
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from kj_atlas_api.access_control import AuthContext
from kj_atlas_api.auth_context import ResolvedIdentity
from kj_atlas_api.db import get_db
from kj_atlas_api.main import app
from kj_atlas_api.models import Base, TenantMembershipRow, TenantRow, UserRow
from kj_atlas_api.session_context import CapabilitySnapshot
from kj_atlas_api.tenant_context import (
    SingleTenantContextResolver,
    TenantContext,
    select_active_tenant_context,
)


TIMESTAMP = "2026-07-17T00:00:00Z"


@dataclass
class StaticIdentityResolver:
    principal_id: str | None = "user-1"

    def resolve(self, *, db: Session, request: Request) -> ResolvedIdentity:  # noqa: ARG002
        actor_ref = (
            f"secret-reviewer:{self.principal_id}"
            if self.principal_id is not None
            else None
        )
        return ResolvedIdentity(
            user_id=self.principal_id,
            reviewer_ref=actor_ref,
            owner_ref=actor_ref,
            auth_context=AuthContext(
                actor_ref=actor_ref,
                user_id=self.principal_id,
                provider="secret-idp",
                external_uid="secret-subject",
                roles=("secret-role",),
                groups=("secret-group",),
                trace_id=None,
            ),
        )


@dataclass
class MutableTenantResolver:
    tenant_id: str = "tenant-a"
    resolved_by: str = "verified_claim"
    membership_id_override: str | None = None

    def resolve(self, *, db: Session, user_id: str | None) -> TenantContext:
        if self.membership_id_override is not None:
            return TenantContext(
                tenant_id=self.tenant_id,
                membership_id=self.membership_id_override,
                resolved_by=self.resolved_by,  # type: ignore[arg-type]
            )
        if user_id is not None and self.resolved_by in {
            "verified_claim",
            "trusted_host_mapping",
        }:
            selected = select_active_tenant_context(
                db=db,
                user_id=user_id,
                tenant_id=self.tenant_id,
                resolved_by=self.resolved_by,  # type: ignore[arg-type]
            )
            return TenantContext(
                tenant_id=selected.tenant_id,
                membership_id=self.membership_id_override or selected.membership_id,
                resolved_by=selected.resolved_by,
            )
        return TenantContext(
            tenant_id=self.tenant_id,
            membership_id=self.membership_id_override or f"membership-{self.tenant_id}",
            resolved_by=self.resolved_by,  # type: ignore[arg-type]
        )


@dataclass
class MutableCapabilityResolver:
    capabilities: tuple[str, ...] = ("document.write", "document.read")
    capability_version: str = "capability-v7"
    calls: int = 0

    def resolve(
        self,
        *,
        db: Session,  # noqa: ARG002
        principal_id: str,  # noqa: ARG002
        tenant: TenantContext,  # noqa: ARG002
    ) -> CapabilitySnapshot:
        self.calls += 1
        return CapabilitySnapshot(
            effective_capabilities=self.capabilities,
            capability_version=self.capability_version,
        )


class RaisingTenantResolver:
    def resolve(self, *, db: Session, user_id: str | None) -> TenantContext:  # noqa: ARG002
        raise RuntimeError("secret tenant resolver failure")


def _seed(db: Session) -> None:
    db.add(
        UserRow(
            id="user-1",
            display_name="Hidden User Name",
            email="hidden@example.invalid",
            lifecycle_state="active",
            created_at=TIMESTAMP,
            updated_at=TIMESTAMP,
        )
    )
    for tenant_id, display_name in (
        ("tenant-b", "Tenant B"),
        ("tenant-a", "Tenant A"),
    ):
        db.add(
            TenantRow(
                id=tenant_id,
                display_name=display_name,
                lifecycle_state="active",
                created_at=TIMESTAMP,
                updated_at=TIMESTAMP,
            )
        )
        db.add(
            TenantMembershipRow(
                tenant_id=tenant_id,
                user_id="user-1",
                lifecycle_state="active",
                created_at=TIMESTAMP,
                updated_at=TIMESTAMP,
            )
        )
    db.commit()


@contextmanager
def _session_client(
    tmp_path,
) -> Iterator[
    tuple[
        TestClient,
        sessionmaker[Session],
        StaticIdentityResolver,
        MutableTenantResolver,
        MutableCapabilityResolver,
    ]
]:
    engine = create_engine(f"sqlite:///{tmp_path / 'session-context.sqlite3'}")
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

    identity_resolver = StaticIdentityResolver()
    tenant_resolver = MutableTenantResolver()
    capability_resolver = MutableCapabilityResolver()
    app.dependency_overrides[get_db] = _get_test_db
    try:
        with TestClient(app) as client:
            client.app.state.saas_identity_context_resolver = identity_resolver
            client.app.state.tenant_context_resolver = tenant_resolver
            client.app.state.tenant_capability_resolver = capability_resolver
            yield (
                client,
                session_local,
                identity_resolver,
                tenant_resolver,
                capability_resolver,
            )
    finally:
        app.dependency_overrides.clear()
        app.state.saas_identity_context_resolver = None
        app.state.tenant_capability_resolver = None
        app.state.tenant_context_resolver = SingleTenantContextResolver()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_context_returns_only_allowlisted_tenants_and_trusted_capabilities(tmp_path) -> None:
    with _session_client(tmp_path) as fixture:
        client, _, _, _, _ = fixture

        response = client.get(
            "/session/context",
            headers={
                "x-tenant-id": "attacker-tenant",
                "x-auth-roles": "platform-admin",
                "x-auth-groups": "platform-operators",
            },
        )

    assert response.status_code == 200
    assert response.json() == {
        "principalId": "user-1",
        "activeTenant": {"id": "tenant-a", "displayName": "Tenant A"},
        "availableTenants": [
            {"id": "tenant-a", "displayName": "Tenant A"},
            {"id": "tenant-b", "displayName": "Tenant B"},
        ],
        "effectiveCapabilities": ["document.read", "document.write"],
        "capabilityVersion": "capability-v7",
    }
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["pragma"] == "no-cache"
    response_text = response.text
    for secret_value in (
        "Hidden User Name",
        "hidden@example.invalid",
        "secret-idp",
        "secret-subject",
        "secret-role",
        "secret-group",
        "attacker-tenant",
        "platform-admin",
    ):
        assert secret_value not in response_text
    assert "membership-" not in response_text


def test_context_is_closed_without_trusted_identity_resolver(tmp_path) -> None:
    with _session_client(tmp_path) as fixture:
        client, _, _, _, _ = fixture
        client.app.state.saas_identity_context_resolver = None

        response = client.get("/session/context")

    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "tenant_admin_auth_unavailable"
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["pragma"] == "no-cache"


def test_context_requires_authenticated_principal(tmp_path) -> None:
    with _session_client(tmp_path) as fixture:
        client, _, identity_resolver, _, _ = fixture
        identity_resolver.principal_id = None

        response = client.get("/session/context")

    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "session_auth_required"


@pytest.mark.parametrize("resolved_by", ["single_tenant_adapter", "client_header"])
def test_context_rejects_untrusted_tenant_resolution_method(
    tmp_path,
    resolved_by: str,
) -> None:
    with _session_client(tmp_path) as fixture:
        client, _, _, tenant_resolver, _ = fixture
        tenant_resolver.resolved_by = resolved_by

        response = client.get("/session/context")

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "tenant_context_untrusted"


def test_context_is_closed_without_capability_resolver(tmp_path) -> None:
    with _session_client(tmp_path) as fixture:
        client, _, _, _, _ = fixture
        client.app.state.tenant_capability_resolver = None

        response = client.get("/session/context")

    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "capability_resolution_unavailable"


def test_context_rejects_unknown_capability(tmp_path) -> None:
    with _session_client(tmp_path) as fixture:
        client, _, _, _, capability_resolver = fixture
        capability_resolver.capabilities = ("document.read", "tenant.root")

        response = client.get("/session/context")

    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "capability_resolution_unavailable"


def test_context_rechecks_active_tenant_membership(tmp_path) -> None:
    with _session_client(tmp_path) as fixture:
        client, session_local, _, tenant_resolver, _ = fixture
        with session_local() as db:
            selected = select_active_tenant_context(
                db=db,
                user_id="user-1",
                tenant_id="tenant-a",
                resolved_by="verified_claim",
            )
            tenant_resolver.membership_id_override = selected.membership_id
            membership = db.get(TenantMembershipRow, ("tenant-a", "user-1"))
            assert membership is not None
            membership.lifecycle_state = "suspended"
            db.commit()

        response = client.get("/session/context")

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "tenant_context_untrusted"


def test_context_rejects_substituted_membership_before_capability_resolution(
    tmp_path,
) -> None:
    with _session_client(tmp_path) as fixture:
        client, _, _, tenant_resolver, capability_resolver = fixture
        tenant_resolver.membership_id_override = "membership-substituted"

        response = client.get("/session/context")

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "tenant_context_untrusted"
    assert capability_resolver.calls == 0


def test_context_normalizes_unexpected_tenant_resolver_failure(tmp_path) -> None:
    with _session_client(tmp_path) as fixture:
        client, _, _, _, _ = fixture
        client.app.state.tenant_context_resolver = RaisingTenantResolver()

        response = client.get("/session/context")

    assert response.status_code == 503
    assert response.json()["detail"] == {
        "code": "tenant_context_resolution_unavailable",
        "message": "Tenant context resolution is unavailable.",
    }
    assert "secret tenant resolver failure" not in response.text
