"""
Create unmatched prompts table.

Revision ID: be3611411d53
Revises: b1a5b6c728fa
Create Date: 2024-02-24 20:15:35.488098

"""
from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa
from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "be3611411d53"
down_revision: str | None = "b1a5b6c728fa"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TABLE_NAME = "unmatched_prompts"


def upgrade() -> None:
    op.create_table(
        TABLE_NAME,
        sa.Column("org_code", sa.String(), primary_key=True),
        sa.Column("prompt_id", sa.UUID(), primary_key=True),
        sa.Column("prompt", sa.String(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table(TABLE_NAME)
