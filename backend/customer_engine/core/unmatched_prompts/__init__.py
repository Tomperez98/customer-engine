"""Unmatched prompts module."""
from __future__ import annotations

from customer_engine.core.unmatched_prompts import (
    add_as_example_to_automatic_response,
    delete,
    get,
    list,
    register,
)

__all__ = ["get", "register", "delete", "add_as_example_to_automatic_response", "list"]
