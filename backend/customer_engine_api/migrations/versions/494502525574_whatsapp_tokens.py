"""
whatsapp tokens.

Revision ID: 494502525574
Revises: be3611411d53
Create Date: 2024-03-04 16:55:10.362184

"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa
from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "494502525574"
down_revision: str | None = "be3611411d53"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


TABLE_NAME = "whatsapp_tokens"


def upgrade() -> None:
    op.create_table(
        TABLE_NAME,
        sa.Column("org_code", sa.String(), primary_key=True),
        sa.Column("access_token", sa.String(), nullable=False),
        sa.Column("user_token", sa.String(), nullable=False),
        sa.Column("phone_number_id", sa.Integer(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table(TABLE_NAME)
