"""ADR-0063 D9-1: add protocol/jwks_uri to identity_providers,
external_tenant_ref to tenant_identity_providers.

- protocol: discriminator for OIDC vs future SAML. Default 'oidc'.
  Accepted values in v1 are {'oidc'} only; unknown values fail-closed.
- jwks_uri: nullable. When present, validated at write time against the
  trusted-HTTP-endpoint contract (loopback prohibited, HTTPS required,
  no credential/query/fragment).
- external_tenant_ref: the organization reference from the identity
  provider's claim — maps into tenants.id via unique(idp_id, ref).
  Nullable: not all idp rows need a tenant binding.

Revision ID: 20260807_0014
Revises: 20260806_0014
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260807_0014"
down_revision: str | None = "20260806_0014"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "identity_providers",
        sa.Column("protocol", sa.Text(), nullable=False, server_default="oidc"),
    )
    op.add_column(
        "identity_providers",
        sa.Column("jwks_uri", sa.Text(), nullable=True),
    )
    op.add_column(
        "tenant_identity_providers",
        sa.Column(
            "external_tenant_ref",
            sa.Text(),
            nullable=True,
        ),
    )
    op.create_unique_constraint(
        "uq_tenant_identity_providers_idp_ref",
        "tenant_identity_providers",
        ["identity_provider_id", "external_tenant_ref"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_tenant_identity_providers_idp_ref",
        "tenant_identity_providers",
        type_="unique",
    )
    op.drop_column("tenant_identity_providers", "external_tenant_ref")
    op.drop_column("identity_providers", "jwks_uri")
    op.drop_column("identity_providers", "protocol")
