"""
Create automatic response table.

Revision ID: 83649af6bbf4
Revises: 10fd71881a3a
Create Date: 2024-02-23 17:27:44.690124

"""
from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa
from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "83649af6bbf4"
down_revision: str | None = "10fd71881a3a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TABLE_NAME = "automatic_responses"


def upgrade() -> None:
    op.create_table(
        TABLE_NAME,
        sa.Column("org_code", sa.String(), primary_key=True),
        sa.Column("automatic_response_id", sa.UUID(), primary_key=True),
        sa.Column("name", sa.String(length=40), nullable=False),
        sa.Column("examples", sa.JSON(), nullable=False),
        sa.Column("embedding_model", sa.String(), nullable=False),
        sa.Column("response", sa.String(length=200), nullable=False),
    )


def downgrade() -> None:
    op.drop_table(TABLE_NAME)
