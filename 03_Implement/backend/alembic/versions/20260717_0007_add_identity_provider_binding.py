"""expand user identities with identity provider binding

Revision ID: 20260717_0007
Revises: 20260716_0006
Create Date: 2026-07-17 00:00:00.000000
"""

from collections.abc import Sequence
from hashlib import sha256

import sqlalchemy as sa
from alembic import op

revision: str = "20260717_0007"
down_revision: str | None = "20260716_0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

LOCAL_DEFAULT_TENANT_ID = "local-default"
LEGACY_IDENTITY_PROVIDER_AUDIENCE = "kj-atlas-single-tenant"
MIGRATION_TIMESTAMP = "2026-07-17T00:00:00Z"
NEW_UNIQUE_NAME = "uq_user_identities_identity_provider_subject"
NEW_FOREIGN_KEY_NAME = "fk_user_identities_identity_provider_id"


def _column_names(inspector: sa.Inspector, table_name: str) -> set[str]:
    return {column["name"] for column in inspector.get_columns(table_name)}


def _index_names(inspector: sa.Inspector, table_name: str) -> set[str]:
    return {index["name"] for index in inspector.get_indexes(table_name)}


def _constraint_names(inspector: sa.Inspector, table_name: str) -> set[str]:
    return {
        constraint["name"]
        for constraint in inspector.get_unique_constraints(table_name)
        if constraint["name"] is not None
    }


def _legacy_binding(provider: str) -> tuple[str, str]:
    normalized_provider = provider.strip().lower()
    if not normalized_provider:
        raise RuntimeError("user_identities.provider must be non-empty before identity binding")
    digest = sha256(normalized_provider.encode("utf-8")).hexdigest()[:24]
    return f"idp-legacy-{digest}", f"urn:kj-atlas:legacy-provider:{digest}"


def _backfill_identity_bindings(bind: sa.Connection) -> None:
    providers = bind.execute(
        sa.text("SELECT DISTINCT provider FROM user_identities ORDER BY provider")
    ).scalars()
    for raw_provider in providers:
        identity_provider_id, issuer = _legacy_binding(str(raw_provider))
        normalized_provider = str(raw_provider).strip().lower()
        existing = bind.execute(
            sa.text(
                "SELECT issuer, audience FROM identity_providers WHERE id = :provider_id"
            ),
            {"provider_id": identity_provider_id},
        ).first()
        if existing is None:
            bind.execute(
                sa.text(
                    """
                    INSERT INTO identity_providers (
                        id, issuer, audience, lifecycle_state, created_at, updated_at
                    ) VALUES (
                        :provider_id, :issuer, :audience, 'active', :created_at, :updated_at
                    )
                    """
                ),
                {
                    "provider_id": identity_provider_id,
                    "issuer": issuer,
                    "audience": LEGACY_IDENTITY_PROVIDER_AUDIENCE,
                    "created_at": MIGRATION_TIMESTAMP,
                    "updated_at": MIGRATION_TIMESTAMP,
                },
            )
        elif tuple(existing) != (issuer, LEGACY_IDENTITY_PROVIDER_AUDIENCE):
            raise RuntimeError("legacy identity provider identifier collision")

        bind.execute(
            sa.text(
                """
                INSERT INTO tenant_identity_providers (
                    tenant_id, identity_provider_id, lifecycle_state, created_at, updated_at
                )
                SELECT :tenant_id, :provider_id, 'active', :created_at, :updated_at
                WHERE NOT EXISTS (
                    SELECT 1 FROM tenant_identity_providers
                    WHERE tenant_id = :tenant_id
                      AND identity_provider_id = :provider_id
                )
                """
            ),
            {
                "tenant_id": LOCAL_DEFAULT_TENANT_ID,
                "provider_id": identity_provider_id,
                "created_at": MIGRATION_TIMESTAMP,
                "updated_at": MIGRATION_TIMESTAMP,
            },
        )
        bind.execute(
            sa.text(
                """
                UPDATE user_identities
                SET identity_provider_id = :provider_id,
                    subject = external_uid
                WHERE lower(trim(provider)) = :normalized_provider
                """
            ),
            {
                "provider_id": identity_provider_id,
                "normalized_provider": normalized_provider,
            },
        )


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("user_identities"):
        return

    columns = _column_names(inspector, "user_identities")
    if "identity_provider_id" not in columns:
        op.add_column(
            "user_identities",
            sa.Column("identity_provider_id", sa.Text(), nullable=True),
        )
    if "subject" not in columns:
        op.add_column(
            "user_identities",
            sa.Column("subject", sa.Text(), nullable=True),
        )

    inspector = sa.inspect(bind)
    if bind.dialect.name != "sqlite":
        foreign_keys = {
            foreign_key["name"]
            for foreign_key in inspector.get_foreign_keys("user_identities")
            if foreign_key["name"] is not None
        }
        if NEW_FOREIGN_KEY_NAME not in foreign_keys:
            op.create_foreign_key(
                NEW_FOREIGN_KEY_NAME,
                "user_identities",
                "identity_providers",
                ["identity_provider_id"],
                ["id"],
                ondelete="RESTRICT",
            )

    _backfill_identity_bindings(bind)

    inspector = sa.inspect(bind)
    unique_names = _constraint_names(inspector, "user_identities") | _index_names(
        inspector, "user_identities"
    )
    if NEW_UNIQUE_NAME not in unique_names:
        op.create_index(
            NEW_UNIQUE_NAME,
            "user_identities",
            ["identity_provider_id", "subject"],
            unique=True,
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("user_identities"):
        return

    if NEW_UNIQUE_NAME in (
        _constraint_names(inspector, "user_identities")
        | _index_names(inspector, "user_identities")
    ):
        op.drop_index(NEW_UNIQUE_NAME, table_name="user_identities")

    inspector = sa.inspect(bind)
    if bind.dialect.name != "sqlite":
        foreign_keys = {
            foreign_key["name"]
            for foreign_key in inspector.get_foreign_keys("user_identities")
            if foreign_key["name"] is not None
        }
        if NEW_FOREIGN_KEY_NAME in foreign_keys:
            op.drop_constraint(
                NEW_FOREIGN_KEY_NAME,
                "user_identities",
                type_="foreignkey",
            )

    columns = _column_names(sa.inspect(bind), "user_identities")
    if "subject" in columns:
        op.drop_column("user_identities", "subject")
    if "identity_provider_id" in columns:
        op.drop_column("user_identities", "identity_provider_id")

    bind.execute(
        sa.text(
            """
            DELETE FROM tenant_identity_providers
            WHERE identity_provider_id LIKE 'idp-legacy-%'
            """
        )
    )
    bind.execute(
        sa.text(
            """
            DELETE FROM identity_providers
            WHERE id LIKE 'idp-legacy-%'
              AND audience = :audience
            """
        ),
        {"audience": LEGACY_IDENTITY_PROVIDER_AUDIENCE},
    )
