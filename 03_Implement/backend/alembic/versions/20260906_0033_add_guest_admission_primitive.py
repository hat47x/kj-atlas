"""add ADR-0080 guest admission primitive

Revision ID: 20260906_0033
Revises: 20260822_0032

Adds a tenant-scoped guest identity and exact document grants without creating
TenantMembership rows. PostgreSQL RLS is enabled in the same migration so a
new tenant-scoped table cannot land outside the data-plane guard.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260906_0033"
down_revision: str | None = "20260822_0032"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _enable_rls(table_name: str, policy_name: str) -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    op.execute(sa.text(f'ALTER TABLE "{table_name}" ENABLE ROW LEVEL SECURITY'))
    op.execute(sa.text(f'ALTER TABLE "{table_name}" FORCE ROW LEVEL SECURITY'))
    op.execute(
        sa.text(
            f'CREATE POLICY "{policy_name}" ON "{table_name}" '
            "USING (tenant_id = NULLIF(current_setting('kj_atlas.tenant_id', true), '')) "
            "WITH CHECK (tenant_id = NULLIF(current_setting('kj_atlas.tenant_id', true), ''))"
        )
    )


def upgrade() -> None:
    op.create_table(
        "guest_principals",
        sa.Column("tenant_id", sa.String(128), nullable=False),
        sa.Column("guest_principal_id", sa.String(128), nullable=False),
        sa.Column("invited_email", sa.String(320), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("verification_method", sa.String(32), nullable=False),
        sa.Column("verified_issuer", sa.String(512), nullable=True),
        sa.Column("verified_subject", sa.String(512), nullable=True),
        sa.Column("created_by", sa.String(512), nullable=False),
        sa.Column("created_at", sa.String(40), nullable=False),
        sa.Column("expires_at", sa.String(40), nullable=False),
        sa.Column("redeemed_at", sa.String(40), nullable=True),
        sa.Column("revoked_at", sa.String(40), nullable=True),
        sa.PrimaryKeyConstraint("tenant_id", "guest_principal_id", name="pk_guest_principals"),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
            name="fk_guest_principals_tenant",
            ondelete="NO ACTION",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "invited_email",
            name="uq_guest_principals_tenant_email",
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'active', 'revoked')",
            name="ck_guest_principals_status",
        ),
        sa.CheckConstraint(
            "verification_method IN ('home_org_idp', 'personal_account')",
            name="ck_guest_principals_verification_method",
        ),
        sa.CheckConstraint(
            "(status = 'pending' AND verified_issuer IS NULL "
            "AND verified_subject IS NULL AND redeemed_at IS NULL AND revoked_at IS NULL) OR "
            "(status = 'active' AND verified_issuer IS NOT NULL "
            "AND verified_subject IS NOT NULL AND redeemed_at IS NOT NULL AND revoked_at IS NULL) OR "
            "(status = 'revoked' AND revoked_at IS NOT NULL)",
            name="ck_guest_principals_lifecycle_shape",
        ),
    )

    op.create_table(
        "guest_document_grants",
        sa.Column("tenant_id", sa.String(128), nullable=False),
        sa.Column("guest_principal_id", sa.String(128), nullable=False),
        sa.Column("doc_id", sa.String(128), nullable=False),
        sa.Column("granted_by", sa.String(512), nullable=False),
        sa.Column("granted_at", sa.String(40), nullable=False),
        sa.Column("revoked_at", sa.String(40), nullable=True),
        sa.PrimaryKeyConstraint(
            "tenant_id",
            "guest_principal_id",
            "doc_id",
            name="pk_guest_document_grants",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "guest_principal_id"],
            ["guest_principals.tenant_id", "guest_principals.guest_principal_id"],
            name="fk_guest_document_grants_principal",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "doc_id"],
            ["documents.tenant_id", "documents.id"],
            name="fk_guest_document_grants_document",
            ondelete="CASCADE",
        ),
    )

    # PostgreSQL can enforce verified guest identity uniqueness without making
    # NULL pending identities collide. Other supported databases retain the
    # repository-level duplicate check until an equivalent portable filtered
    # index contract is settled.
    if op.get_bind().dialect.name == "postgresql":
        op.execute(
            sa.text(
                "CREATE UNIQUE INDEX uq_guest_principals_verified_identity "
                "ON guest_principals (tenant_id, verified_issuer, verified_subject) "
                "WHERE verified_subject IS NOT NULL"
            )
        )

    _enable_rls("guest_principals", "guest_principals_tenant_isolation")
    _enable_rls("guest_document_grants", "guest_document_grants_tenant_isolation")


def downgrade() -> None:
    if op.get_bind().dialect.name == "postgresql":
        op.execute(
            sa.text(
                "DROP POLICY IF EXISTS guest_document_grants_tenant_isolation "
                "ON guest_document_grants"
            )
        )
        op.execute(
            sa.text(
                "DROP POLICY IF EXISTS guest_principals_tenant_isolation ON guest_principals"
            )
        )
        op.execute(sa.text("DROP INDEX IF EXISTS uq_guest_principals_verified_identity"))
    op.drop_table("guest_document_grants")
    op.drop_table("guest_principals")
