"""ADR-0063 D9-4: unit tests for ClaimBasedTenantContextResolver."""

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
    ClaimBasedTenantContextResolver,
    VerifiedTenantClaim,
)

TIMESTAMP = "2026-08-07T00:00:00Z"


def _seed(db: Session) -> None:
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
            TenantRow(
                id="tenant-a",
                display_name="Tenant A",
                lifecycle_state="active",
                created_at=TIMESTAMP,
                updated_at=TIMESTAMP,
            ),
            IdentityProviderRow(
                id="idp-1",
                issuer="https://broker.invalid/issuer",
                audience="kj-atlas",
                protocol="oidc",
                jwks_uri="https://broker.invalid/jwks.json",
                lifecycle_state="active",
                created_at=TIMESTAMP,
                updated_at=TIMESTAMP,
            ),
            TenantIdentityProviderRow(
                tenant_id="tenant-a",
                identity_provider_id="idp-1",
                external_tenant_ref="org-123",
                lifecycle_state="active",
                created_at=TIMESTAMP,
                updated_at=TIMESTAMP,
            ),
            UserIdentityRow(
                user_id="user-1",
                provider="idp-1",
                external_uid="subject-1",
                identity_provider_id="idp-1",
                subject="subject-1",
                created_at=TIMESTAMP,
            ),
            TenantMembershipRow(
                tenant_id="tenant-a",
                user_id="user-1",
                lifecycle_state="active",
                created_at=TIMESTAMP,
                updated_at=TIMESTAMP,
            ),
        ]
    )
    db.commit()


@pytest.fixture
def db() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        _seed(session)
        yield session


class TestClaimBasedTenantContextResolver:
    def test_resolve_with_valid_claim_returns_tenant_context(self, db: Session) -> None:
        resolver = ClaimBasedTenantContextResolver()
        claim = VerifiedTenantClaim(
            tenant_id="tenant-a",
            identity_provider_id="idp-1",
            issuer="https://broker.invalid/issuer",
            audience="kj-atlas",
            subject="subject-1",
        )
        ctx = resolver.resolve(db=db, user_id="user-1", claim=claim)
        assert ctx.tenant_id == "tenant-a"
        assert ctx.resolved_by == "verified_claim"

    def test_resolve_without_claim_is_denied(self, db: Session) -> None:
        resolver = ClaimBasedTenantContextResolver()
        with pytest.raises(HTTPException) as exc:
            resolver.resolve(db=db, user_id="user-1", claim=None)
        assert exc.value.status_code == 403
        assert exc.value.detail["code"] == "tenant_context_untrusted"

    def test_resolve_with_claim_none_is_denied(self, db: Session) -> None:
        resolver = ClaimBasedTenantContextResolver()
        with pytest.raises(HTTPException) as exc:
            resolver.resolve(db=db, user_id="user-1")
        assert exc.value.status_code == 403

    def test_resolve_with_mismatched_issuer_is_denied(self, db: Session) -> None:
        resolver = ClaimBasedTenantContextResolver()
        claim = VerifiedTenantClaim(
            tenant_id="tenant-a",
            identity_provider_id="idp-1",
            issuer="https://evil.invalid/issuer",
            audience="kj-atlas",
            subject="subject-1",
        )
        with pytest.raises(HTTPException) as exc:
            resolver.resolve(db=db, user_id="user-1", claim=claim)
        assert exc.value.status_code == 403

    def test_resolve_with_unknown_tenant_is_denied(self, db: Session) -> None:
        resolver = ClaimBasedTenantContextResolver()
        claim = VerifiedTenantClaim(
            tenant_id="tenant-unknown",
            identity_provider_id="idp-1",
            issuer="https://broker.invalid/issuer",
            audience="kj-atlas",
            subject="subject-1",
        )
        with pytest.raises(HTTPException) as exc:
            resolver.resolve(db=db, user_id="user-1", claim=claim)
        assert exc.value.status_code == 403

    def test_resolve_with_no_membership_is_denied(self, db: Session) -> None:
        resolver = ClaimBasedTenantContextResolver()
        claim = VerifiedTenantClaim(
            tenant_id="tenant-a",
            identity_provider_id="idp-1",
            issuer="https://broker.invalid/issuer",
            audience="kj-atlas",
            subject="subject-1",
        )
        with pytest.raises(HTTPException) as exc:
            resolver.resolve(db=db, user_id="user-unknown", claim=claim)
        assert exc.value.status_code == 403
