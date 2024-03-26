"""
Add org settings.

Revision ID: c556d6cf4749
Revises: 494502525574
Create Date: 2024-03-25 16:21:37.230006

"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa
from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "c556d6cf4749"
down_revision: str | None = "494502525574"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TABLE_NAME = "org_settings"


def upgrade() -> None:
    op.create_table(
        TABLE_NAME,
        sa.Column("org_code", sa.String(), primary_key=True),
        sa.Column("default_response", sa.String(), nullable=False),
        sa.Column("embeddings_model", sa.String(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table(TABLE_NAME)
