"""Automatic responses module."""

from __future__ import annotations

from customer_engine_api.handlers.automatic_responses import (
    create_auto_resp,
    create_example,
    delete_auto_res,
    delete_bulk_examples,
    delete_example,
    get_auto_res,
    get_auto_res_owns_example,
    get_bulk_examples,
    get_example,
    list_auto_res,
    list_examples,
    similar_examples_by_prompt,
    update_auto_res,
    update_example,
)

__all__ = [
    "create_auto_resp",
    "create_example",
    "delete_auto_res",
    "delete_bulk_examples",
    "delete_example",
    "get_auto_res",
    "get_auto_res_owns_example",
    "get_bulk_examples",
    "get_example",
    "list_auto_res",
    "list_examples",
    "similar_examples_by_prompt",
    "update_auto_res",
    "update_example",
]
