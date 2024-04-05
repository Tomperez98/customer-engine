"""
Automatic responses owns examples.

Revision ID: 62525831f106
Revises: c556d6cf4749
Create Date: 2024-03-25 20:07:42.744839

"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa
from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "62525831f106"
down_revision: str | None = "c556d6cf4749"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

AUTOMATIC_RESPONSE_TABLE = "automatic_responses"

TABLE_NAME = "automatic_response_examples"


def upgrade() -> None:
    op.create_table(
        TABLE_NAME,
        sa.Column("org_code", sa.String(), primary_key=True),
        sa.Column("example_id", sa.UUID(), primary_key=True),
        sa.Column("automatic_response_id", sa.UUID()),
        sa.Column("example", sa.String(), nullable=False),
    )
    op.create_index(
        index_name=None,
        table_name=TABLE_NAME,
        columns=["org_code", "automatic_response_id"],
    )


def downgrade() -> None:
    raise NotImplementedError
