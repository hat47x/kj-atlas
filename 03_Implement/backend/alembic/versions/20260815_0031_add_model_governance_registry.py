"""add model governance registry (AI-MODEL-GOVERNANCE-01 R1/R3)

Revision ID: 20260815_0031
Revises: 20260815_0030

- llm_provider_registry: dynamic provider/service registry (platform-shared)
- llm_model_registry: canonical model registry owned by a provider
- tenant_model_allowlist: tenant-scoped model allowlist (R3, fail-closed)
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260815_0031"
down_revision: str | None = "20260815_0030"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "llm_provider_registry",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("provider_kind", sa.Text(), nullable=False),
        sa.Column("display_name", sa.Text(), nullable=False),
        sa.Column("base_url", sa.Text(), nullable=True),
        sa.Column("api_key_ref", sa.Text(), nullable=True),
        sa.Column("lifecycle_state", sa.Text(), nullable=False),
        sa.Column("created_at", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "llm_model_registry",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("provider_id", sa.Text(), nullable=False),
        sa.Column("display_name", sa.Text(), nullable=False),
        sa.Column("capabilities", sa.Text(), nullable=True),
        sa.Column("lifecycle_state", sa.Text(), nullable=False),
        sa.Column("created_at", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["provider_id"],
            ["llm_provider_registry.id"],
            name="fk_llm_model_registry_provider",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "tenant_model_allowlist",
        sa.Column("tenant_id", sa.Text(), nullable=False),
        sa.Column("model_id", sa.Text(), nullable=False),
        sa.Column("lifecycle_state", sa.Text(), nullable=False),
        sa.Column("created_at", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["model_id"], ["llm_model_registry.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("tenant_id", "model_id"),
    )
    if op.get_bind().dialect.name == "postgresql":
        tenant_using = "tenant_id = NULLIF(current_setting('kj_atlas.tenant_id', true), '')"
        op.execute(sa.text("ALTER TABLE tenant_model_allowlist ENABLE ROW LEVEL SECURITY"))
        op.execute(sa.text("ALTER TABLE tenant_model_allowlist FORCE ROW LEVEL SECURITY"))
        op.execute(
            sa.text(
                "CREATE POLICY tenant_model_allowlist_tenant ON tenant_model_allowlist "
                f"USING ({tenant_using}) WITH CHECK ({tenant_using})"
            )
        )


def downgrade() -> None:
    if op.get_bind().dialect.name == "postgresql":
        op.execute(sa.text("DROP POLICY IF EXISTS tenant_model_allowlist_tenant ON tenant_model_allowlist"))
    op.drop_table("tenant_model_allowlist")
    op.drop_table("llm_model_registry")
    op.drop_table("llm_provider_registry")
