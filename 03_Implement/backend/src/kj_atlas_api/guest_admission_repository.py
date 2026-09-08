from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from kj_atlas_api.guest_admission_models import GuestDocumentGrantRow, GuestPrincipalRow
from kj_atlas_api.models import DocumentRow
from kj_atlas_api.tenant_db_guard import apply_database_tenant_id


class GuestAdmissionError(ValueError):
    """Rejected guest-admission state transition or malformed trusted input."""


def _required(value: str, *, field: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise GuestAdmissionError(f"{field} must be non-empty")
    return normalized


def _normalized_email(value: str) -> str:
    return _required(value, field="invited_email").casefold()


def _parse_aware_timestamp(value: str) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed.astimezone(timezone.utc)


def _aware_utc(now: datetime) -> datetime:
    if now.tzinfo is None or now.utcoffset() is None:
        raise GuestAdmissionError("now must be timezone-aware")
    return now.astimezone(timezone.utc)


class GuestAdmissionRepository:
    """ADR-0080 exact-grant guest primitive.

    Every operation reapplies the transaction-local tenant guard. Guest
    principals never become TenantMembership rows, and there is deliberately no
    tenant-wide fallback: an active principal can read only an exact, unrevoked
    ``guest_document_grants`` row.
    """

    def __init__(self, db: Session, *, tenant_id: str) -> None:
        self._db = db
        self._tenant_id = _required(tenant_id, field="tenant_id")

    @property
    def tenant_id(self) -> str:
        return self._tenant_id

    def _scope(self) -> None:
        apply_database_tenant_id(db=self._db, tenant_id=self._tenant_id)

    def create_pending_guest(
        self,
        *,
        guest_principal_id: str,
        invited_email: str,
        verification_method: str,
        created_by: str,
        created_at: str,
        expires_at: str,
        now: datetime,
    ) -> GuestPrincipalRow:
        self._scope()
        principal_id = _required(guest_principal_id, field="guest_principal_id")
        email = _normalized_email(invited_email)
        method = _required(verification_method, field="verification_method")
        if method not in {"home_org_idp", "personal_account"}:
            raise GuestAdmissionError("unsupported verification_method")
        expiry = _parse_aware_timestamp(expires_at)
        if expiry is None or expiry <= _aware_utc(now):
            raise GuestAdmissionError("expires_at must be a future aware timestamp")
        if self._db.get(GuestPrincipalRow, (self._tenant_id, principal_id)) is not None:
            raise GuestAdmissionError("guest_principal_id already exists")
        duplicate_email = self._db.scalar(
            select(GuestPrincipalRow)
            .where(GuestPrincipalRow.tenant_id == self._tenant_id)
            .where(GuestPrincipalRow.invited_email == email)
            .limit(1)
        )
        if duplicate_email is not None:
            raise GuestAdmissionError("invited_email already exists in tenant")
        row = GuestPrincipalRow(
            tenant_id=self._tenant_id,
            guest_principal_id=principal_id,
            invited_email=email,
            status="pending",
            verification_method=method,
            verified_issuer=None,
            verified_subject=None,
            created_by=_required(created_by, field="created_by"),
            created_at=_required(created_at, field="created_at"),
            expires_at=expires_at,
            redeemed_at=None,
            revoked_at=None,
        )
        self._db.add(row)
        self._db.flush()
        return row

    def activate_verified_guest(
        self,
        *,
        guest_principal_id: str,
        verified_issuer: str,
        verified_subject: str,
        redeemed_at: str,
        now: datetime,
    ) -> GuestPrincipalRow:
        self._scope()
        principal_id = _required(guest_principal_id, field="guest_principal_id")
        row = self._db.get(GuestPrincipalRow, (self._tenant_id, principal_id))
        if row is None or row.status != "pending":
            raise GuestAdmissionError("guest principal is not pending")
        expiry = _parse_aware_timestamp(row.expires_at)
        if expiry is None or expiry <= _aware_utc(now):
            raise GuestAdmissionError("guest invitation is expired or malformed")
        issuer = _required(verified_issuer, field="verified_issuer")
        subject = _required(verified_subject, field="verified_subject")
        duplicate_identity = self._db.scalar(
            select(GuestPrincipalRow)
            .where(GuestPrincipalRow.tenant_id == self._tenant_id)
            .where(GuestPrincipalRow.verified_issuer == issuer)
            .where(GuestPrincipalRow.verified_subject == subject)
            .where(GuestPrincipalRow.guest_principal_id != principal_id)
            .limit(1)
        )
        if duplicate_identity is not None:
            raise GuestAdmissionError("verified identity already belongs to another guest")
        row.status = "active"
        row.verified_issuer = issuer
        row.verified_subject = subject
        row.redeemed_at = _required(redeemed_at, field="redeemed_at")
        self._db.flush()
        return row

    def grant_document(
        self,
        *,
        guest_principal_id: str,
        doc_id: str,
        granted_by: str,
        granted_at: str,
    ) -> GuestDocumentGrantRow:
        self._scope()
        principal_id = _required(guest_principal_id, field="guest_principal_id")
        normalized_doc_id = _required(doc_id, field="doc_id")
        principal = self._db.get(GuestPrincipalRow, (self._tenant_id, principal_id))
        if principal is None or principal.status == "revoked":
            raise GuestAdmissionError("guest principal is not grantable")
        if self._db.get(DocumentRow, (self._tenant_id, normalized_doc_id)) is None:
            raise GuestAdmissionError("document does not exist in tenant")
        key = (self._tenant_id, principal_id, normalized_doc_id)
        existing = self._db.get(GuestDocumentGrantRow, key)
        if existing is not None:
            if existing.revoked_at is None:
                return existing
            raise GuestAdmissionError("revoked grant cannot be silently resurrected")
        row = GuestDocumentGrantRow(
            tenant_id=self._tenant_id,
            guest_principal_id=principal_id,
            doc_id=normalized_doc_id,
            granted_by=_required(granted_by, field="granted_by"),
            granted_at=_required(granted_at, field="granted_at"),
            revoked_at=None,
        )
        self._db.add(row)
        self._db.flush()
        return row

    def can_read_document(self, *, guest_principal_id: str, doc_id: str) -> bool:
        self._scope()
        principal_id = _required(guest_principal_id, field="guest_principal_id")
        normalized_doc_id = _required(doc_id, field="doc_id")
        principal = self._db.get(GuestPrincipalRow, (self._tenant_id, principal_id))
        if principal is None or principal.status != "active" or principal.revoked_at is not None:
            return False
        grant = self._db.get(
            GuestDocumentGrantRow,
            (self._tenant_id, principal_id, normalized_doc_id),
        )
        return grant is not None and grant.revoked_at is None

    def list_readable_document_ids(self, *, guest_principal_id: str) -> tuple[str, ...]:
        self._scope()
        principal_id = _required(guest_principal_id, field="guest_principal_id")
        principal = self._db.get(GuestPrincipalRow, (self._tenant_id, principal_id))
        if principal is None or principal.status != "active" or principal.revoked_at is not None:
            return ()
        return tuple(
            self._db.scalars(
                select(GuestDocumentGrantRow.doc_id)
                .where(GuestDocumentGrantRow.tenant_id == self._tenant_id)
                .where(GuestDocumentGrantRow.guest_principal_id == principal_id)
                .where(GuestDocumentGrantRow.revoked_at.is_(None))
                .order_by(GuestDocumentGrantRow.doc_id.asc())
            ).all()
        )

    def revoke_document_grant(
        self,
        *,
        guest_principal_id: str,
        doc_id: str,
        revoked_at: str,
    ) -> bool:
        self._scope()
        grant = self._db.get(
            GuestDocumentGrantRow,
            (
                self._tenant_id,
                _required(guest_principal_id, field="guest_principal_id"),
                _required(doc_id, field="doc_id"),
            ),
        )
        if grant is None or grant.revoked_at is not None:
            return False
        grant.revoked_at = _required(revoked_at, field="revoked_at")
        self._db.flush()
        return True

    def revoke_guest_principal(
        self,
        *,
        guest_principal_id: str,
        revoked_at: str,
    ) -> bool:
        self._scope()
        principal = self._db.get(
            GuestPrincipalRow,
            (self._tenant_id, _required(guest_principal_id, field="guest_principal_id")),
        )
        if principal is None or principal.status == "revoked":
            return False
        principal.status = "revoked"
        principal.revoked_at = _required(revoked_at, field="revoked_at")
        self._db.flush()
        return True
