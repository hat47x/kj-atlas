from __future__ import annotations

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from kj_atlas_api.models import (
    Base,
    IdentityProviderRow,
    TenantIdentityProviderRow,
    TenantMembershipRow,
    TenantRow,
    UserIdentityRow,
    UserRow,
)
from kj_atlas_api.tenant_context import (
    VerifiedTenantClaim,
    list_active_tenant_summaries,
    resolve_verified_claim_tenant_context,
    select_active_tenant_context,
)


TIMESTAMP = "2026-07-17T00:00:00Z"


def _seed_verified_identity(db: Session) -> None:
    db.add_all(
        [
            UserRow(
                id="user-1",
                display_name="User 1",
                email=None,
                lifecycle_state="active",
                created_at=TIMESTAMP,
                updated_at=TIMESTAMP,
            ),
            UserRow(
                id="user-2",
                display_name="User 2",
                email=None,
                lifecycle_state="active",
                created_at=TIMESTAMP,
                updated_at=TIMESTAMP,
            ),
            TenantRow(
                id="tenant-a",
                display_name="Tenant A",
                lifecycle_state="active",
                created_at=TIMESTAMP,
                updated_at=TIMESTAMP,
            ),
            TenantRow(
                id="tenant-b",
                display_name="Tenant B",
                lifecycle_state="active",
                created_at=TIMESTAMP,
                updated_at=TIMESTAMP,
            ),
            TenantRow(
                id="tenant-suspended",
                display_name="Tenant Suspended",
                lifecycle_state="suspended",
                created_at=TIMESTAMP,
                updated_at=TIMESTAMP,
            ),
            IdentityProviderRow(
                id="idp-1",
                issuer="https://issuer.example.test/",
                audience="kj-atlas",
                lifecycle_state="active",
                created_at=TIMESTAMP,
                updated_at=TIMESTAMP,
            ),
        ]
    )
    db.commit()
    db.add_all(
        [
            TenantIdentityProviderRow(
                tenant_id="tenant-a",
                identity_provider_id="idp-1",
                lifecycle_state="active",
                created_at=TIMESTAMP,
                updated_at=TIMESTAMP,
            ),
            TenantMembershipRow(
                tenant_id="tenant-a",
                user_id="user-1",
                lifecycle_state="active",
                created_at=TIMESTAMP,
                updated_at=TIMESTAMP,
            ),
            TenantMembershipRow(
                tenant_id="tenant-b",
                user_id="user-1",
                lifecycle_state="active",
                created_at=TIMESTAMP,
                updated_at=TIMESTAMP,
            ),
            TenantMembershipRow(
                tenant_id="tenant-suspended",
                user_id="user-1",
                lifecycle_state="active",
                created_at=TIMESTAMP,
                updated_at=TIMESTAMP,
            ),
            UserIdentityRow(
                user_id="user-1",
                provider="oidc",
                external_uid="subject-1",
                identity_provider_id="idp-1",
                subject="subject-1",
                created_at=TIMESTAMP,
            ),
        ]
    )
    db.commit()


def _claim(**overrides: str) -> VerifiedTenantClaim:
    values = {
        "tenant_id": "tenant-a",
        "identity_provider_id": "idp-1",
        "issuer": "https://issuer.example.test/",
        "audience": "kj-atlas",
        "subject": "subject-1",
    }
    values.update(overrides)
    return VerifiedTenantClaim(**values)


def test_verified_claim_resolves_active_bound_membership() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    try:
        with Session(engine) as db:
            _seed_verified_identity(db)
            context = resolve_verified_claim_tenant_context(
                db=db,
                user_id="user-1",
                claim=_claim(),
            )

        assert context.tenant_id == "tenant-a"
        assert context.membership_id is not None
        assert context.resolved_by == "verified_claim"
    finally:
        engine.dispose()


@pytest.mark.parametrize(
    "claim",
    [
        _claim(issuer="https://attacker.example.test/"),
        _claim(audience="other-service"),
        _claim(identity_provider_id="missing-idp"),
        _claim(tenant_id="tenant-b"),
        _claim(subject="unknown-subject"),
    ],
)
def test_untrusted_claim_variants_are_indistinguishably_denied(
    claim: VerifiedTenantClaim,
) -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    try:
        with Session(engine) as db:
            _seed_verified_identity(db)
            with pytest.raises(HTTPException) as exc_info:
                resolve_verified_claim_tenant_context(
                    db=db,
                    user_id="user-1",
                    claim=claim,
                )

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == {
            "code": "tenant_context_untrusted",
            "message": "Verified tenant context is required.",
        }
    finally:
        engine.dispose()


def test_claim_identity_must_match_authenticated_user() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    try:
        with Session(engine) as db:
            _seed_verified_identity(db)
            with pytest.raises(HTTPException) as exc_info:
                resolve_verified_claim_tenant_context(
                    db=db,
                    user_id="user-2",
                    claim=_claim(),
                )

        assert exc_info.value.detail["code"] == "tenant_context_untrusted"
    finally:
        engine.dispose()


def test_available_tenants_are_membership_allowlist_only() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    try:
        with Session(engine) as db:
            _seed_verified_identity(db)
            summaries = list_active_tenant_summaries(db=db, user_id="user-1")

        assert [(item.tenant_id, item.display_name) for item in summaries] == [
            ("tenant-a", "Tenant A"),
            ("tenant-b", "Tenant B"),
        ]
    finally:
        engine.dispose()


def test_active_tenant_selection_rechecks_membership_and_hides_others() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    try:
        with Session(engine) as db:
            _seed_verified_identity(db)
            selected = select_active_tenant_context(
                db=db,
                user_id="user-1",
                tenant_id="tenant-b",
                resolved_by="verified_claim",
            )
            assert selected.tenant_id == "tenant-b"

            for unavailable_tenant in ("tenant-suspended", "unknown-tenant"):
                with pytest.raises(HTTPException) as exc_info:
                    select_active_tenant_context(
                        db=db,
                        user_id="user-1",
                        tenant_id=unavailable_tenant,
                        resolved_by="verified_claim",
                    )
                assert exc_info.value.status_code == 404
                assert exc_info.value.detail == {
                    "code": "tenant_not_available",
                    "message": "Requested tenant is not available.",
                }
    finally:
        engine.dispose()
