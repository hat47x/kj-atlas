from __future__ import annotations

from sqlalchemy import ForeignKeyConstraint, Index, Text
from sqlalchemy.orm import Mapped, mapped_column

from kj_atlas_api.guest_admission_models import GuestPrincipalRow  # noqa: F401
from kj_atlas_api.models import Base
from kj_atlas_api.persistence_shapes import apply_persistent_text_shapes


class GuestRedeemStateRow(Base):
    """One-time pre-tenant handle binding an invitation to guest login.

    The raw handle is never persisted. This row is intentionally pre-tenant
    authentication state: it must be found from the opaque handle before the
    tenant is known. After resolution, callers immediately apply the normal
    transaction-local tenant guard before touching the guest principal.
    """

    __tablename__ = "guest_redeem_states"
    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "guest_principal_id"],
            ["guest_principals.tenant_id", "guest_principals.guest_principal_id"],
            name="fk_guest_redeem_states_principal",
            ondelete="CASCADE",
        ),
        Index("ix_guest_redeem_states_principal", "tenant_id", "guest_principal_id"),
    )

    state_key_hash: Mapped[str] = mapped_column(Text, primary_key=True)
    tenant_id: Mapped[str] = mapped_column(Text, nullable=False)
    guest_principal_id: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(Text, nullable=False)
    expires_at: Mapped[str] = mapped_column(Text, nullable=False)
    consumed_at: Mapped[str | None] = mapped_column(Text, nullable=True)


apply_persistent_text_shapes(Base.metadata)
