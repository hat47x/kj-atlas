"""add recoverable inline content blob payload

Revision ID: 20260811_0021
Revises: 20260810_0020
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

from kj_atlas_api.persistence_shapes import portable_binary_lob_type

revision: str = "20260811_0021"
down_revision: str | None = "20260810_0020"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_TABLE = "content_blobs"
_CONSTRAINT = "ck_content_blobs_payload_location"
_PAYLOAD_LOCATION = (
    "(storage_backend = 'database' AND locator IS NULL "
    "AND (storage_state != 'ready' OR payload_bytes IS NOT NULL)) OR "
    "(storage_backend IN ('nas', 's3', 'git') AND locator IS NOT NULL "
    "AND length(trim(locator)) > 0 AND payload_bytes IS NULL)"
)


def upgrade() -> None:
    bind = op.get_bind()
    with op.batch_alter_table(_TABLE) as batch_op:
        batch_op.add_column(sa.Column("payload_bytes", portable_binary_lob_type(), nullable=True))

    # Metadata created before this revision never contained recoverable bytes.
    # Do not invent content or leave it advertised as ready.
    bind.execute(
        sa.text(
            "UPDATE content_blobs SET storage_state = 'failed' "
            "WHERE storage_backend = 'database' AND storage_state = 'ready'"
        )
    )
    expression = _PAYLOAD_LOCATION
    if bind.dialect.name == "mssql":
        expression = expression.replace("length(", "len(")
    with op.batch_alter_table(_TABLE) as batch_op:
        batch_op.create_check_constraint(_CONSTRAINT, expression)


def downgrade() -> None:
    with op.batch_alter_table(_TABLE) as batch_op:
        batch_op.drop_constraint(_CONSTRAINT, type_="check")
        batch_op.drop_column("payload_bytes")
