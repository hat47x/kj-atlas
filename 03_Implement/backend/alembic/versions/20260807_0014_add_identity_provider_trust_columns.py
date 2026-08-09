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

_MYSQL_IDP_FK_INDEX = "ix_tenant_identity_providers_identity_provider_id"


def _has_index(bind: sa.Connection, index_name: str) -> bool:
    return any(
        index["name"] == index_name
        for index in sa.inspect(bind).get_indexes("tenant_identity_providers")
    )


def upgrade() -> None:
    bind = op.get_bind()
    # ADD COLUMN works on both SQLite and PostgreSQL.
    op.add_column(
        "identity_providers",
        sa.Column("protocol", sa.String(32), nullable=False, server_default="oidc"),
    )
    op.add_column(
        "identity_providers",
        sa.Column("jwks_uri", sa.String(2048), nullable=True),
    )
    op.add_column(
        "tenant_identity_providers",
        sa.Column(
            "external_tenant_ref",
            sa.String(512),
            nullable=True,
        ),
    )
    # CREATE UNIQUE CONSTRAINT: use batch mode for SQLite compatibility.
    # SQLite does not support ALTER TABLE ADD CONSTRAINT; batch mode
    # transparently uses a copy-and-move strategy for SQLite while
    # emitting native ALTER on PostgreSQL.
    with op.batch_alter_table("tenant_identity_providers") as batch_op:
        batch_op.create_unique_constraint(
            "uq_tenant_identity_providers_idp_ref",
            ["identity_provider_id", "external_tenant_ref"],
        )
    if bind.dialect.name in {"mysql", "mariadb"} and _has_index(bind, _MYSQL_IDP_FK_INDEX):
        op.drop_index(_MYSQL_IDP_FK_INDEX, table_name="tenant_identity_providers")


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name in {"mysql", "mariadb"} and not _has_index(bind, _MYSQL_IDP_FK_INDEX):
        op.create_index(
            _MYSQL_IDP_FK_INDEX,
            "tenant_identity_providers",
            ["identity_provider_id"],
        )
    with op.batch_alter_table("tenant_identity_providers") as batch_op:
        batch_op.drop_constraint(
            "uq_tenant_identity_providers_idp_ref",
            type_="unique",
        )
    op.drop_column("tenant_identity_providers", "external_tenant_ref")
    op.drop_column("identity_providers", "jwks_uri")
    op.drop_column("identity_providers", "protocol")
