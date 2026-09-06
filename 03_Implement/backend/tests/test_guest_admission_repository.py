from __future__ import annotations

from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine, event, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from kj_atlas_api.guest_admission_models import GuestDocumentGrantRow, GuestPrincipalRow
from kj_atlas_api.guest_admission_repository import GuestAdmissionError, GuestAdmissionRepository
from kj_atlas_api.models import Base, DocumentRow, TenantMembershipRow, TenantRow

NOW = datetime(2026, 9, 6, 12, 0, 0, tzinfo=timezone.utc)
CREATED_AT = "2026-09-06T12:00:00Z"
EXPIRES_AT = "2026-09-07T12:00:00Z"
REDEEMED_AT = "2026-09-06T12:05:00Z"
REVOKED_AT = "2026-09-06T12:10:00Z"


def _engine():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)

    @event.listens_for(engine, "connect")
    def _enable_foreign_keys(dbapi_connection, _connection_record) -> None:  # noqa: ANN001
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    return engine


def _seed(db: Session) -> None:
    for tenant_id in ("tenant-a", "tenant-b"):
        db.add(
            TenantRow(
                id=tenant_id,
                display_name=tenant_id,
                lifecycle_state="active",
                created_at=CREATED_AT,
                updated_at=CREATED_AT,
            )
        )
    db.flush()
    for tenant_id, doc_id in (
        ("tenant-a", "doc-a"),
        ("tenant-a", "doc-a-other"),
        ("tenant-b", "doc-b-only"),
    ):
        db.add(
            DocumentRow(
                tenant_id=tenant_id,
                id=doc_id,
                version=1,
                updated_at=CREATED_AT,
                payload_json="{}",
            )
        )
    db.commit()


def _pending(repo: GuestAdmissionRepository, *, principal_id: str = "guest-1") -> GuestPrincipalRow:
    return repo.create_pending_guest(
        guest_principal_id=principal_id,
        invited_email=f"{principal_id}@example.test",
        verification_method="personal_account",
        created_by="host-admin",
        created_at=CREATED_AT,
        expires_at=EXPIRES_AT,
        now=NOW,
    )


def _activate(repo: GuestAdmissionRepository, *, principal_id: str = "guest-1") -> GuestPrincipalRow:
    return repo.activate_verified_guest(
        guest_principal_id=principal_id,
        verified_issuer="https://accounts.example.test",
        verified_subject=f"subject-{principal_id}",
        redeemed_at=REDEEMED_AT,
        now=NOW,
    )


def test_principal_existence_alone_never_creates_membership_or_document_visibility() -> None:
    engine = _engine()
    with Session(engine) as db:
        _seed(db)
        repo = GuestAdmissionRepository(db, tenant_id="tenant-a")
        _pending(repo)
        _activate(repo)

        assert repo.list_readable_document_ids(guest_principal_id="guest-1") == ()
        assert repo.can_read_document(guest_principal_id="guest-1", doc_id="doc-a") is False
        assert db.scalars(select(TenantMembershipRow)).all() == []


def test_pending_grant_is_inert_until_redeem_then_only_exact_grant_is_visible() -> None:
    engine = _engine()
    with Session(engine) as db:
        _seed(db)
        repo = GuestAdmissionRepository(db, tenant_id="tenant-a")
        _pending(repo)
        repo.grant_document(
            guest_principal_id="guest-1",
            doc_id="doc-a",
            granted_by="host-admin",
            granted_at=CREATED_AT,
        )

        assert repo.can_read_document(guest_principal_id="guest-1", doc_id="doc-a") is False
        assert repo.list_readable_document_ids(guest_principal_id="guest-1") == ()

        _activate(repo)
        assert repo.can_read_document(guest_principal_id="guest-1", doc_id="doc-a") is True
        assert repo.can_read_document(guest_principal_id="guest-1", doc_id="doc-a-other") is False
        assert repo.list_readable_document_ids(guest_principal_id="guest-1") == ("doc-a",)


def test_expired_pending_guest_cannot_be_activated() -> None:
    engine = _engine()
    with Session(engine) as db:
        _seed(db)
        repo = GuestAdmissionRepository(db, tenant_id="tenant-a")
        repo.create_pending_guest(
            guest_principal_id="expired-guest",
            invited_email="expired@example.test",
            verification_method="home_org_idp",
            created_by="host-admin",
            created_at="2026-09-05T00:00:00Z",
            expires_at="2026-09-06T11:59:59Z",
            now=datetime(2026, 9, 6, 11, 0, tzinfo=timezone.utc),
        )
        with pytest.raises(GuestAdmissionError, match="expired"):
            repo.activate_verified_guest(
                guest_principal_id="expired-guest",
                verified_issuer="https://idp.example.test",
                verified_subject="expired-subject",
                redeemed_at=CREATED_AT,
                now=NOW,
            )
        assert repo.list_readable_document_ids(guest_principal_id="expired-guest") == ()


def test_tenant_can_revoke_one_grant_without_guest_action_and_effect_is_immediate() -> None:
    engine = _engine()
    with Session(engine) as db:
        _seed(db)
        repo = GuestAdmissionRepository(db, tenant_id="tenant-a")
        _pending(repo)
        _activate(repo)
        repo.grant_document(
            guest_principal_id="guest-1",
            doc_id="doc-a",
            granted_by="host-admin",
            granted_at=CREATED_AT,
        )
        assert repo.can_read_document(guest_principal_id="guest-1", doc_id="doc-a") is True

        assert repo.revoke_document_grant(
            guest_principal_id="guest-1",
            doc_id="doc-a",
            revoked_at=REVOKED_AT,
        ) is True
        assert repo.can_read_document(guest_principal_id="guest-1", doc_id="doc-a") is False
        assert repo.list_readable_document_ids(guest_principal_id="guest-1") == ()
        with pytest.raises(GuestAdmissionError, match="silently resurrected"):
            repo.grant_document(
                guest_principal_id="guest-1",
                doc_id="doc-a",
                granted_by="host-admin",
                granted_at="2026-09-06T12:11:00Z",
            )


def test_tenant_can_revoke_principal_without_guest_action_and_all_grants_stop_immediately() -> None:
    engine = _engine()
    with Session(engine) as db:
        _seed(db)
        repo = GuestAdmissionRepository(db, tenant_id="tenant-a")
        _pending(repo)
        _activate(repo)
        for doc_id in ("doc-a", "doc-a-other"):
            repo.grant_document(
                guest_principal_id="guest-1",
                doc_id=doc_id,
                granted_by="host-admin",
                granted_at=CREATED_AT,
            )
        assert repo.list_readable_document_ids(guest_principal_id="guest-1") == (
            "doc-a",
            "doc-a-other",
        )

        assert repo.revoke_guest_principal(
            guest_principal_id="guest-1",
            revoked_at=REVOKED_AT,
        ) is True
        assert repo.list_readable_document_ids(guest_principal_id="guest-1") == ()
        assert repo.can_read_document(guest_principal_id="guest-1", doc_id="doc-a") is False
        principal = db.get(GuestPrincipalRow, ("tenant-a", "guest-1"))
        assert principal is not None and principal.status == "revoked"
        assert db.get(GuestDocumentGrantRow, ("tenant-a", "guest-1", "doc-a")) is not None


def test_composite_foreign_keys_reject_cross_tenant_document_grant_even_without_repository_filter() -> None:
    engine = _engine()
    with Session(engine) as db:
        _seed(db)
        repo = GuestAdmissionRepository(db, tenant_id="tenant-a")
        _pending(repo)
        db.add(
            GuestDocumentGrantRow(
                tenant_id="tenant-a",
                guest_principal_id="guest-1",
                doc_id="doc-b-only",
                granted_by="host-admin",
                granted_at=CREATED_AT,
                revoked_at=None,
            )
        )
        with pytest.raises(IntegrityError):
            db.flush()
        db.rollback()


def test_invited_email_is_canonicalized_and_deduplicated_within_tenant() -> None:
    engine = _engine()
    with Session(engine) as db:
        _seed(db)
        repo = GuestAdmissionRepository(db, tenant_id="tenant-a")
        repo.create_pending_guest(
            guest_principal_id="guest-1",
            invited_email="  Person@Example.Test ",
            verification_method="personal_account",
            created_by="host-admin",
            created_at=CREATED_AT,
            expires_at=EXPIRES_AT,
            now=NOW,
        )
        with pytest.raises(GuestAdmissionError, match="invited_email already exists"):
            repo.create_pending_guest(
                guest_principal_id="guest-2",
                invited_email="person@example.test",
                verification_method="personal_account",
                created_by="host-admin",
                created_at=CREATED_AT,
                expires_at=EXPIRES_AT,
                now=NOW,
            )
