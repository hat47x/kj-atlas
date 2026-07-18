from __future__ import annotations

from dataclasses import dataclass

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from kj_atlas_api.models import Base, TenantMembershipRow, TenantRow, UserRow
from kj_atlas_api.session_context import (
    CapabilitySnapshot,
    build_tenant_session_context,
    switch_tenant_session_context,
)
from kj_atlas_api.tenant_context import (
    TenantContext,
    TenantSummary,
    select_active_tenant_context,
)


TIMESTAMP = "2026-07-17T00:00:00Z"


@dataclass
class StubCapabilityResolver:
    snapshot: CapabilitySnapshot
    calls: int = 0
    last_tenant_id: str | None = None

    def resolve(
        self,
        *,
        db: Session,  # noqa: ARG002
        principal_id: str,  # noqa: ARG002
        tenant: TenantContext,  # noqa: ARG002
    ) -> CapabilitySnapshot:
        self.calls += 1
        self.last_tenant_id = tenant.tenant_id
        return self.snapshot


class RaisingCapabilityResolver:
    def resolve(
        self,
        *,
        db: Session,  # noqa: ARG002
        principal_id: str,  # noqa: ARG002
        tenant: TenantContext,  # noqa: ARG002
    ) -> CapabilitySnapshot:
        raise RuntimeError("policy backend unavailable")


def _seed(db: Session) -> None:
    db.add(
        UserRow(
            id="user-1",
            display_name="User 1",
            email=None,
            lifecycle_state="active",
            created_at=TIMESTAMP,
            updated_at=TIMESTAMP,
        )
    )
    for tenant_id, display_name, lifecycle_state in (
        ("tenant-a", "Tenant A", "active"),
        ("tenant-b", "Tenant B", "active"),
        ("tenant-suspended", "Tenant Suspended", "suspended"),
    ):
        db.add(
            TenantRow(
                id=tenant_id,
                display_name=display_name,
                lifecycle_state=lifecycle_state,
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


def _tenant(db: Session, tenant_id: str = "tenant-a") -> TenantContext:
    return select_active_tenant_context(
        db=db,
        user_id="user-1",
        tenant_id=tenant_id,
        resolved_by="verified_claim",
    )


def _stale_tenant(tenant_id: str = "tenant-suspended") -> TenantContext:
    return TenantContext(
        tenant_id=tenant_id,
        membership_id="membership-opaque",
        resolved_by="verified_claim",
    )


def test_builds_context_from_active_memberships_and_trusted_capabilities() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    resolver = StubCapabilityResolver(
        CapabilitySnapshot(
            effective_capabilities=("document.write", "document.read"),
            capability_version="policy-v7",
        )
    )
    try:
        with Session(engine) as db:
            _seed(db)
            context = build_tenant_session_context(
                db=db,
                principal_id="user-1",
                tenant=_tenant(db),
                capability_resolver=resolver,
            )

        assert context.principal_id == "user-1"
        assert context.tenant_context.tenant_id == "tenant-a"
        assert context.tenant_context.membership_id is not None
        assert context.tenant_context.membership_id.startswith("membership-")
        assert (context.active_tenant.tenant_id, context.active_tenant.display_name) == (
            "tenant-a",
            "Tenant A",
        )
        assert [tenant.tenant_id for tenant in context.available_tenants] == [
            "tenant-a",
            "tenant-b",
        ]
        assert context.effective_capabilities == ("document.read", "document.write")
        assert context.capability_version == "policy-v7"
        assert resolver.calls == 1
    finally:
        engine.dispose()


def test_anonymous_session_is_rejected_before_capability_resolution() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    resolver = StubCapabilityResolver(CapabilitySnapshot((), "policy-v1"))
    try:
        with Session(engine) as db:
            with pytest.raises(HTTPException) as exc_info:
                build_tenant_session_context(
                    db=db,
                    principal_id=None,
                    tenant=_stale_tenant("tenant-a"),
                    capability_resolver=resolver,
                )

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail["code"] == "session_auth_required"
        assert resolver.calls == 0
    finally:
        engine.dispose()


@pytest.mark.parametrize("principal_id", [" user-1", "x" * 257, "user\u200b1"])
def test_noncanonical_principal_fails_before_tenant_or_capability_resolution(
    principal_id: str,
) -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    resolver = StubCapabilityResolver(CapabilitySnapshot((), "policy-v1"))
    try:
        with Session(engine) as db:
            with pytest.raises(HTTPException) as exc_info:
                build_tenant_session_context(
                    db=db,
                    principal_id=principal_id,
                    tenant=_stale_tenant("tenant-a"),
                    capability_resolver=resolver,
                )

        assert exc_info.value.status_code == 503
        assert exc_info.value.detail["code"] == "session_context_unavailable"
        assert resolver.calls == 0
    finally:
        engine.dispose()


def test_oversized_tenant_allowlist_fails_before_capability_resolution(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    resolver = StubCapabilityResolver(CapabilitySnapshot((), "policy-v1"))
    try:
        with Session(engine) as db:
            _seed(db)
            monkeypatch.setattr(
                "kj_atlas_api.session_context.list_active_tenant_summaries",
                lambda db, user_id, limit: tuple(  # noqa: ARG005
                    TenantSummary(
                        tenant_id=f"tenant-{index}",
                        display_name=f"Tenant {index}",
                    )
                    for index in range(257)
                )[:limit],
            )
            with pytest.raises(HTTPException) as exc_info:
                build_tenant_session_context(
                    db=db,
                    principal_id="user-1",
                    tenant=_tenant(db),
                    capability_resolver=resolver,
                )

        assert exc_info.value.status_code == 503
        assert exc_info.value.detail["code"] == "session_context_unavailable"
        assert resolver.calls == 0
    finally:
        engine.dispose()


def test_stale_or_unavailable_active_tenant_is_rejected_before_policy_call() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    resolver = StubCapabilityResolver(CapabilitySnapshot((), "policy-v1"))
    try:
        with Session(engine) as db:
            _seed(db)
            with pytest.raises(HTTPException) as exc_info:
                build_tenant_session_context(
                    db=db,
                    principal_id="user-1",
                    tenant=_stale_tenant(),
                    capability_resolver=resolver,
                )

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail["code"] == "tenant_context_untrusted"
        assert resolver.calls == 0
    finally:
        engine.dispose()


def test_substituted_membership_evidence_is_rejected_before_policy_call() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    resolver = StubCapabilityResolver(CapabilitySnapshot((), "policy-v1"))
    try:
        with Session(engine) as db:
            _seed(db)
            with pytest.raises(HTTPException) as exc_info:
                build_tenant_session_context(
                    db=db,
                    principal_id="user-1",
                    tenant=TenantContext(
                        tenant_id="tenant-a",
                        membership_id="membership-substituted",
                        resolved_by="verified_claim",
                    ),
                    capability_resolver=resolver,
                )

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail["code"] == "tenant_context_untrusted"
        assert resolver.calls == 0
    finally:
        engine.dispose()


@pytest.mark.parametrize(
    "snapshot",
    [
        CapabilitySnapshot((" document.read",), "policy-v1"),
        CapabilitySnapshot(("document.read\n",), "policy-v1"),
        CapabilitySnapshot(("tenant.root",), "policy-v1"),
        CapabilitySnapshot(("document.read", "document.read"), "policy-v1"),
        CapabilitySnapshot(("document.read",), "x" * 129),
        CapabilitySnapshot(("document.read\u200b",), "policy-v1"),
        CapabilitySnapshot(("document.read",), ""),
    ],
)
def test_invalid_policy_snapshot_fails_closed(snapshot: CapabilitySnapshot) -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    resolver = StubCapabilityResolver(snapshot)
    try:
        with Session(engine) as db:
            _seed(db)
            with pytest.raises(HTTPException) as exc_info:
                build_tenant_session_context(
                    db=db,
                    principal_id="user-1",
                    tenant=_tenant(db),
                    capability_resolver=resolver,
                )

        assert exc_info.value.status_code == 503
        assert exc_info.value.detail == {
            "code": "capability_resolution_unavailable",
            "message": "Tenant capabilities are unavailable.",
        }
    finally:
        engine.dispose()


def test_policy_resolver_error_is_normalized_without_leaking_details() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    try:
        with Session(engine) as db:
            _seed(db)
            with pytest.raises(HTTPException) as exc_info:
                build_tenant_session_context(
                    db=db,
                    principal_id="user-1",
                    tenant=_tenant(db),
                    capability_resolver=RaisingCapabilityResolver(),
                )

        assert exc_info.value.status_code == 503
        assert exc_info.value.detail == {
            "code": "capability_resolution_unavailable",
            "message": "Tenant capabilities are unavailable.",
        }
    finally:
        engine.dispose()


def test_switch_rechecks_allowlist_then_resolves_capabilities_for_new_tenant() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    resolver = StubCapabilityResolver(CapabilitySnapshot(("document.read",), "policy-v2"))
    try:
        with Session(engine) as db:
            _seed(db)
            context = switch_tenant_session_context(
                db=db,
                principal_id="user-1",
                current_tenant=_tenant(db),
                requested_tenant_id="tenant-b",
                capability_resolver=resolver,
            )

        assert context.active_tenant.tenant_id == "tenant-b"
        assert context.capability_version == "policy-v2"
        assert resolver.calls == 1
        assert resolver.last_tenant_id == "tenant-b"
    finally:
        engine.dispose()


@pytest.mark.parametrize(
    "requested_tenant_id",
    [
        "tenant-suspended",
        "unknown-tenant",
        " tenant-b",
        "tenant-b\n",
        "x" * 257,
        "tenant\u200bb",
    ],
)
def test_switch_hides_unavailable_requested_tenant(
    requested_tenant_id: str,
) -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    resolver = StubCapabilityResolver(CapabilitySnapshot((), "policy-v1"))
    try:
        with Session(engine) as db:
            _seed(db)
            with pytest.raises(HTTPException) as exc_info:
                switch_tenant_session_context(
                    db=db,
                    principal_id="user-1",
                    current_tenant=_tenant(db),
                    requested_tenant_id=requested_tenant_id,
                    capability_resolver=resolver,
                )

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail["code"] == "tenant_not_available"
        assert resolver.calls == 0
    finally:
        engine.dispose()


def test_switch_rejects_single_tenant_or_stale_current_context_before_selection() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    resolver = StubCapabilityResolver(CapabilitySnapshot((), "policy-v1"))
    try:
        with Session(engine) as db:
            _seed(db)
            for current_tenant in (
                TenantContext(
                    tenant_id="tenant-a",
                    membership_id="membership-opaque",
                    resolved_by="single_tenant_adapter",
                ),
                _stale_tenant(),
            ):
                with pytest.raises(HTTPException) as exc_info:
                    switch_tenant_session_context(
                        db=db,
                        principal_id="user-1",
                        current_tenant=current_tenant,
                        requested_tenant_id="tenant-b",
                        capability_resolver=resolver,
                    )
                assert exc_info.value.status_code == 403
                assert exc_info.value.detail["code"] == "tenant_context_untrusted"

        assert resolver.calls == 0
    finally:
        engine.dispose()
