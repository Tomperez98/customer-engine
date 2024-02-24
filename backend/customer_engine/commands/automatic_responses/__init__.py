"""Automatic responses command."""
from __future__ import annotations

from customer_engine.commands.automatic_responses import (
    create,
    delete,
    get,
    list,
    search_by_prompt,
    update,
)

__all__ = [
    "list",
    "create",
    "get",
    "delete",
    "update",
    "search_by_prompt",
]