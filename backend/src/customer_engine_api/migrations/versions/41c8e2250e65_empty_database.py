"""
empty database.

Revision ID: 41c8e2250e65
Revises:
Create Date: 2024-02-13 18:10:55.827049

"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "41c8e2250e65"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None: ...


def downgrade() -> None: ...
