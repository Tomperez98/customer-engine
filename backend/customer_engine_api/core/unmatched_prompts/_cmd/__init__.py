"""Unmatched prompts commands."""

from __future__ import annotations

from customer_engine_api.core.unmatched_prompts._cmd import (
    add_as_example_to_automatic_response,
    delete,
    get,
    list_all,
    register,
)

__all__ = [
    "get",
    "register",
    "delete",
    "add_as_example_to_automatic_response",
    "list_all",
]
