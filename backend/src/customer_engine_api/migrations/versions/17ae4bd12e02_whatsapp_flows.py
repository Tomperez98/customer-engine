"""
whatsapp flows.

Revision ID: 17ae4bd12e02
Revises: 41c8e2250e65
Create Date: 2024-02-13 18:14:01.082856

"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa
from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "17ae4bd12e02"
down_revision: str | None = "41c8e2250e65"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TABLE_NAME = "whatsapp_flows"


def upgrade() -> None:
    op.create_table(
        TABLE_NAME,
        sa.Column("org_code", sa.String(), primary_key=True),
        sa.Column("flow_id", sa.UUID(), primary_key=True),
        sa.Column("name", sa.String(length=40), nullable=False),
        sa.Column("examples", sa.JSON(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table(table_name=TABLE_NAME)
