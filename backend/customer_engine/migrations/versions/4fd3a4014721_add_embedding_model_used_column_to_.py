"""
Add embedding_model_used column to whatsapp_flows table.

Revision ID: 4fd3a4014721
Revises: 17ae4bd12e02
Create Date: 2024-02-14 21:11:43.326370

"""
from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa
from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "4fd3a4014721"
down_revision: str | None = "17ae4bd12e02"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TABLE_NAME = "whatsapp_flows"


def upgrade() -> None:
    op.add_column(
        TABLE_NAME,
        sa.Column(
            "embedding_model",
            sa.String(),
            nullable=False,
            default="embed-multilingual-light-v3.0",
        ),
    )


def downgrade() -> None:
    op.drop_column(TABLE_NAME, "embedding_model")
