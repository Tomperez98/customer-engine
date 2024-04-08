"""Automatic responses core."""

from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Self
from uuid import UUID

from mashumaro.mixins.orjson import DataClassORJSONMixin
from sqlalchemy import Row

from customer_engine_api.core.automatic_responses import _embeddings as embeddings
from customer_engine_api.core.interfaces import SqlQueriable

if TYPE_CHECKING:
    from sqlalchemy import Row

__all__ = ["embeddings"]


@dataclass(frozen=True)
class UnmatchedPrompt(DataClassORJSONMixin, SqlQueriable):
    org_code: str
    prompt_id: UUID
    prompt: str
    created_at: datetime.datetime

    @classmethod
    def from_row(cls: type[Self], row: Row[Any]) -> Self:
        return cls.from_dict(row._asdict())


@dataclass(frozen=True)
class Example(DataClassORJSONMixin, SqlQueriable):
    org_code: str
    example_id: UUID
    automatic_response_id: UUID
    example: str

    @classmethod
    def from_row(cls: type[Self], row: Row[Any]) -> Self:
        return cls.from_dict(row._asdict())

    def update(self, example: str | None) -> Example:
        """Update example."""
        return Example(
            org_code=self.org_code,
            example_id=self.example_id,
            automatic_response_id=self.automatic_response_id,
            example=example if example is not None else self.example,
        )


@dataclass(frozen=True)
class AutomaticResponse(DataClassORJSONMixin, SqlQueriable):
    """Automatic response."""

    org_code: str
    automatic_response_id: UUID
    name: str
    response: str

    @classmethod
    def from_row(cls: type[Self], row: Row[Any]) -> Self:
        """Instantiate from row."""
        return cls.from_dict(row._asdict())

    def update(self, name: str | None, response: str | None) -> AutomaticResponse:
        """Update automatic response."""
        return AutomaticResponse(
            org_code=self.org_code,
            automatic_response_id=self.automatic_response_id,
            name=name if name is not None else self.name,
            response=response if response is not None else self.response,
        )
