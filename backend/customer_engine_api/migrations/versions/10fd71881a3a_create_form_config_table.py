"""
Create form config table.

Revision ID: 10fd71881a3a
Revises: 127d34fd5433
Create Date: 2024-02-15 18:36:11.016534

"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa
from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "10fd71881a3a"
down_revision: str | None = "127d34fd5433"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TABLE_NAME = "form_configs"


def upgrade() -> None:
    op.create_table(
        TABLE_NAME,
        sa.Column("org_code", sa.String(), primary_key=True),
        sa.Column("form_id", sa.UUID(), primary_key=True),
        sa.Column("configuration", sa.JSON(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table(table_name=TABLE_NAME)
