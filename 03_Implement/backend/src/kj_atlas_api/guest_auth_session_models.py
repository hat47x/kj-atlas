from __future__ import annotations

from sqlalchemy import ForeignKeyConstraint, Text
from sqlalchemy.orm import Mapped, mapped_column

from kj_atlas_api.guest_admission_models import GuestPrincipalRow  # noqa: F401
from kj_atlas_api.models import Base
from kj_atlas_api.persistence_shapes import apply_persistent_text_shapes


class GuestAuthSessionRow(Base):
    """Server-owned login session for an ADR-0080 guest principal.

    This table is intentionally separate from ``saas_auth_sessions``: a guest
    is not a tenant member and must never acquire the member auth/session
    semantics merely by having an opaque cookie.  Unlike tenant data tables,
    this row is looked up by a keyed hash *before* the tenant is known, so the
    table itself is not tenant-RLS protected.  Once the row establishes the
    tenant, every principal/grant/document lookup returns to the normal
    transaction-local tenant guard and FORCE-RLS tables.
    """

    __tablename__ = "guest_auth_sessions"
    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "guest_principal_id"],
            ["guest_principals.tenant_id", "guest_principals.guest_principal_id"],
            name="fk_guest_auth_sessions_principal",
            ondelete="CASCADE",
        ),
    )

    session_key_hash: Mapped[str] = mapped_column(Text, primary_key=True)
    tenant_id: Mapped[str] = mapped_column(Text, nullable=False)
    guest_principal_id: Mapped[str] = mapped_column(Text, nullable=False)
    issuer: Mapped[str] = mapped_column(Text, nullable=False)
    subject: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(Text, nullable=False)
    last_used_at: Mapped[str] = mapped_column(Text, nullable=False)
    absolute_expires_at: Mapped[str] = mapped_column(Text, nullable=False)
    revoked_at: Mapped[str | None] = mapped_column(Text, nullable=True)


apply_persistent_text_shapes(Base.metadata)
