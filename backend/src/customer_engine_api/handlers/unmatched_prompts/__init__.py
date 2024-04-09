"""Unmatched prompts handlers."""

from __future__ import annotations

from customer_engine_api.handlers.unmatched_prompts import (
    bulk_add_to_auto_res_as_example,
    bulk_delete_unmatched_prompts,
    delete_all,
    delete_unmatched_prompt,
    get_subset_unmatched_prompts,
    get_unmatched_prompt,
    list_unmatched_prompts,
    register_unmatched_prompt,
)

__all__ = [
    "bulk_add_to_auto_res_as_example",
    "bulk_delete_unmatched_prompts",
    "delete_all",
    "delete_unmatched_prompt",
    "get_subset_unmatched_prompts",
    "get_unmatched_prompt",
    "list_unmatched_prompts",
    "register_unmatched_prompt",
]
