"""
Rename whatsapp flows table to forms.

Revision ID: 127d34fd5433
Revises: 4fd3a4014721
Create Date: 2024-02-15 09:01:46.107922

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "127d34fd5433"
down_revision: str | None = "4fd3a4014721"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        table_name="whatsapp_flows", column_name="flow_id", new_column_name="form_id"
    )
    op.rename_table(old_table_name="whatsapp_flows", new_table_name="forms")


def downgrade() -> None:
    op.alter_column(
        table_name="forms", column_name="form_id", new_column_name="flow_id"
    )
    op.rename_table(old_table_name="forms", new_table_name="whatsapp_flows")
