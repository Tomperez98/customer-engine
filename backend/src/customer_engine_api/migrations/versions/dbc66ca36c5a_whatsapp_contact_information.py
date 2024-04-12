"""
whatsapp contact information.

Revision ID: dbc66ca36c5a
Revises: 5d96388d8dba
Create Date: 2024-04-12 17:20:55.326449

"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa
from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "dbc66ca36c5a"
down_revision: str | None = "5d96388d8dba"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TABLE_NAME = "whatsapp_contacts"


def upgrade() -> None:
    op.create_table(
        TABLE_NAME,
        sa.Column("org_code", sa.String(), primary_key=True),
        sa.Column("wa_id", sa.String(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table(TABLE_NAME)
