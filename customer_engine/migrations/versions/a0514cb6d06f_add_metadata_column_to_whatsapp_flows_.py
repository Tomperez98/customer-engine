"""
Add metadata column to whatsapp_flows table.

Revision ID: a0514cb6d06f
Revises: 17ae4bd12e02
Create Date: 2024-02-13 21:52:57.487742

"""
from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa
from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "a0514cb6d06f"
down_revision: str | None = "17ae4bd12e02"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TABLE_NAME = "whatsapp_flows"
COL_NAME = "metadata"


def upgrade() -> None:
    op.add_column(
        table_name=TABLE_NAME,
        column=sa.Column(COL_NAME, sa.JSON(), nullable=False),
    )


def downgrade() -> None:
    op.drop_column(table_name=TABLE_NAME, column_name=COL_NAME)
