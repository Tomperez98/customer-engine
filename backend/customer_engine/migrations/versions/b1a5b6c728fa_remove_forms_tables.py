"""
remove forms tables.

Revision ID: b1a5b6c728fa
Revises: 83649af6bbf4
Create Date: 2024-02-24 19:04:22.354464

"""
from __future__ import annotations

from typing import TYPE_CHECKING

from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "b1a5b6c728fa"
down_revision: str | None = "83649af6bbf4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_table(table_name="forms")
    op.drop_table(table_name="form_configs")


def downgrade() -> None:
    raise NotImplementedError
