"""
Add time related columns.

Revision ID: 5d96388d8dba
Revises: 62525831f106
Create Date: 2024-04-06 12:08:10.562518

"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa
from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "5d96388d8dba"
down_revision: str | None = "62525831f106"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TABLE_NAME = "unmatched_prompts"


def upgrade() -> None:
    op.add_column(
        table_name=TABLE_NAME,
        column=sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_column(table_name=TABLE_NAME, column_name="created_at")
