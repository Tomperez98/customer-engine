"""Unmatched prompts shared."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Self
from uuid import UUID

from mashumaro.mixins.orjson import DataClassORJSONMixin

from customer_engine_api.core.interfaces import SqlQueriable

if TYPE_CHECKING:
    from sqlalchemy import Row


@dataclass(frozen=True)
class UnmatchedPrompt(
    DataClassORJSONMixin,
    SqlQueriable,
):
    """Unmatched prompt."""

    org_code: str
    prompt_id: UUID
    prompt: str

    @classmethod
    def from_row(cls: type[Self], row: Row[Any]) -> Self:
        """Instantiate class from prompt."""
        return cls.from_dict(row._asdict())
