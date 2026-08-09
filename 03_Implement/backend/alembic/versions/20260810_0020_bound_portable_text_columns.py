"""bound identifier and descriptive text columns for portable indexes

Revision ID: 20260810_0020
Revises: 20260810_0019
"""

from collections import defaultdict
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

from kj_atlas_api.persistence_shapes import PERSISTENT_TEXT_SPECS

revision: str = "20260810_0020"
down_revision: str | None = "20260810_0019"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _suspend_postgres_policies(
    bind: sa.Connection, table_names: set[str]
) -> list[dict[str, object]]:
    if bind.dialect.name != "postgresql" or not table_names:
        return []
    policies = [
        dict(row)
        for row in bind.execute(
            sa.text(
                """
                SELECT policyname, tablename, permissive, roles, cmd, qual, with_check
                FROM pg_policies
                WHERE schemaname = current_schema()
                """
            )
        ).mappings()
        if row["tablename"] in table_names
    ]
    quote = bind.dialect.identifier_preparer.quote
    for policy in policies:
        op.execute(
            sa.text(
                f"DROP POLICY {quote(str(policy['policyname']))} "
                f"ON {quote(str(policy['tablename']))}"
            )
        )
    return policies


def _restore_postgres_policies(bind: sa.Connection, policies: list[dict[str, object]]) -> None:
    quote = bind.dialect.identifier_preparer.quote
    for policy in policies:
        roles = ", ".join(
            "PUBLIC" if str(role).lower() == "public" else quote(str(role))
            for role in policy["roles"] or ["public"]
        )
        statement = (
            f"CREATE POLICY {quote(str(policy['policyname']))} "
            f"ON {quote(str(policy['tablename']))} "
            f"AS {policy['permissive']} FOR {policy['cmd']} TO {roles}"
        )
        if policy["qual"] is not None:
            statement += f" USING ({policy['qual']})"
        if policy["with_check"] is not None:
            statement += f" WITH CHECK ({policy['with_check']})"
        op.execute(sa.text(statement))


def _bounded_columns() -> dict[str, list[tuple[str, int]]]:
    result: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for qualified_name, spec in PERSISTENT_TEXT_SPECS.items():
        if spec.proposed_max_chars is None:
            continue
        table_name, column_name = qualified_name.split(".", 1)
        result[table_name].append((column_name, spec.proposed_max_chars))
    return dict(result)


def _alter(*, bounded: bool) -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())
    bounded_columns = _bounded_columns()
    policies = _suspend_postgres_policies(bind, existing_tables & bounded_columns.keys())
    for table_name, columns in sorted(bounded_columns.items()):
        if table_name not in existing_tables:
            continue
        reflected = {column["name"]: column for column in inspector.get_columns(table_name)}
        with op.batch_alter_table(table_name) as batch_op:
            for column_name, max_chars in sorted(columns):
                existing = reflected.get(column_name)
                if existing is None:
                    continue
                batch_op.alter_column(
                    column_name,
                    existing_type=existing["type"],
                    existing_nullable=existing["nullable"],
                    type_=sa.String(max_chars) if bounded else sa.Text(),
                )
    _restore_postgres_policies(bind, policies)


def _restore_sqlite_expression_indexes() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "sqlite":
        return
    index_name = "uq_user_identities_provider_lower_external_uid"
    indexes = sa.inspect(bind).get_indexes("user_identities")
    if not any(index["name"] == index_name for index in indexes):
        op.create_index(
            index_name,
            "user_identities",
            [sa.text("lower(provider)"), sa.text("lower(external_uid)")],
            unique=True,
        )


def upgrade() -> None:
    _alter(bounded=True)
    _restore_sqlite_expression_indexes()


def downgrade() -> None:
    if op.get_bind().dialect.name in {"mysql", "mariadb", "mssql"}:
        # Fresh MySQL-family and SQL Server schemas were already bounded by the
        # historical DDL hook before this revision, so their 0019 shape is
        # still VARCHAR.
        return
    _alter(bounded=False)
    _restore_sqlite_expression_indexes()
