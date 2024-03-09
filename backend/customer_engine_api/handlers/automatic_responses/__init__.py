"""Automatic responses module."""

from __future__ import annotations

from customer_engine_api.handlers.automatic_responses import (
    create,
    delete,
    get,
    list_all,
    search_by_prompt,
    update,
)

__all__ = ["get", "delete", "create", "list_all", "search_by_prompt", "update"]
