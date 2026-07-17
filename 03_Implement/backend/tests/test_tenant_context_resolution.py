from __future__ import annotations

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from kj_atlas_api.models import (
    Base,
    LOCAL_DEFAULT_TENANT_ID,
    TenantMembershipRow,
    TenantRow,
    UserRow,
)
from kj_atlas_api.tenant_context import resolve_single_tenant_context


TIMESTAMP = "2026-07-17T00:00:00Z"


def _seed_membership(
    db: Session,
    *,
    user_state: str = "active",
    tenant_state: str = "active",
    membership_state: str = "active",
) -> None:
    db.add(
        UserRow(
            id="user-1",
            display_name="User 1",
            email=None,
            lifecycle_state=user_state,
            created_at=TIMESTAMP,
            updated_at=TIMESTAMP,
        )
    )
    db.add(
        TenantRow(
            id=LOCAL_DEFAULT_TENANT_ID,
            display_name="Local workspace",
            lifecycle_state=tenant_state,
            created_at=TIMESTAMP,
            updated_at=TIMESTAMP,
        )
    )
    db.add(
        TenantMembershipRow(
            tenant_id=LOCAL_DEFAULT_TENANT_ID,
            user_id="user-1",
            lifecycle_state=membership_state,
            created_at=TIMESTAMP,
            updated_at=TIMESTAMP,
        )
    )
    db.commit()


def test_anonymous_single_tenant_context_keeps_compatibility() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    try:
        with Session(engine) as db:
            context = resolve_single_tenant_context(db=db, user_id=None)

        assert context.tenant_id == LOCAL_DEFAULT_TENANT_ID
        assert context.membership_id is None
        assert context.resolved_by == "single_tenant_adapter"
    finally:
        engine.dispose()


def test_authenticated_context_requires_active_membership() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    try:
        with Session(engine) as db:
            _seed_membership(db)
            context = resolve_single_tenant_context(db=db, user_id="user-1")

        assert context.tenant_id == LOCAL_DEFAULT_TENANT_ID
        assert context.membership_id is not None
        assert context.membership_id.startswith("membership-")
        assert context.resolved_by == "single_tenant_adapter"
    finally:
        engine.dispose()


@pytest.mark.parametrize(
    ("user_state", "tenant_state", "membership_state"),
    [
        ("suspended", "active", "active"),
        ("active", "suspended", "active"),
        ("active", "active", "suspended"),
    ],
)
def test_inactive_identity_tenant_or_membership_is_denied(
    user_state: str,
    tenant_state: str,
    membership_state: str,
) -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    try:
        with Session(engine) as db:
            _seed_membership(
                db,
                user_state=user_state,
                tenant_state=tenant_state,
                membership_state=membership_state,
            )
            with pytest.raises(HTTPException) as exc_info:
                resolve_single_tenant_context(db=db, user_id="user-1")

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail["code"] == "tenant_membership_inactive"
    finally:
        engine.dispose()


def test_missing_membership_is_denied_without_tenant_discovery() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    try:
        with Session(engine) as db:
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
            db.commit()
            with pytest.raises(HTTPException) as exc_info:
                resolve_single_tenant_context(db=db, user_id="user-1")

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == {
            "code": "tenant_membership_inactive",
            "message": "Active tenant membership is required.",
        }
    finally:
        engine.dispose()
