from __future__ import annotations

from sqlalchemy import CheckConstraint, ForeignKey, ForeignKeyConstraint, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from kj_atlas_api.models import Base


class GuestPrincipalRow(Base):
    """ADR-0080 individual guest identity, intentionally outside membership."""

    __tablename__ = "guest_principals"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "invited_email",
            name="uq_guest_principals_tenant_email",
        ),
        CheckConstraint(
            "status IN ('pending', 'active', 'revoked')",
            name="ck_guest_principals_status",
        ),
        CheckConstraint(
            "verification_method IN ('home_org_idp', 'personal_account')",
            name="ck_guest_principals_verification_method",
        ),
        CheckConstraint(
            "(status = 'pending' AND verified_issuer IS NULL "
            "AND verified_subject IS NULL AND redeemed_at IS NULL AND revoked_at IS NULL) OR "
            "(status = 'active' AND verified_issuer IS NOT NULL "
            "AND verified_subject IS NOT NULL AND redeemed_at IS NOT NULL AND revoked_at IS NULL) OR "
            "(status = 'revoked' AND revoked_at IS NOT NULL)",
            name="ck_guest_principals_lifecycle_shape",
        ),
    )

    tenant_id: Mapped[str] = mapped_column(
        String(128),
        ForeignKey("tenants.id", ondelete="NO ACTION"),
        primary_key=True,
    )
    guest_principal_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    invited_email: Mapped[str] = mapped_column(String(320), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    verification_method: Mapped[str] = mapped_column(String(32), nullable=False)
    verified_issuer: Mapped[str | None] = mapped_column(String(512), nullable=True)
    verified_subject: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_by: Mapped[str] = mapped_column(String(512), nullable=False)
    created_at: Mapped[str] = mapped_column(String(40), nullable=False)
    expires_at: Mapped[str] = mapped_column(String(40), nullable=False)
    redeemed_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
    revoked_at: Mapped[str | None] = mapped_column(String(40), nullable=True)


class GuestDocumentGrantRow(Base):
    """Exact document grant; no row means no guest visibility."""

    __tablename__ = "guest_document_grants"
    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "guest_principal_id"],
            ["guest_principals.tenant_id", "guest_principals.guest_principal_id"],
            name="fk_guest_document_grants_principal",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "doc_id"],
            ["documents.tenant_id", "documents.id"],
            name="fk_guest_document_grants_document",
            ondelete="CASCADE",
        ),
    )

    tenant_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    guest_principal_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    doc_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    granted_by: Mapped[str] = mapped_column(String(512), nullable=False)
    granted_at: Mapped[str] = mapped_column(String(40), nullable=False)
    revoked_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
