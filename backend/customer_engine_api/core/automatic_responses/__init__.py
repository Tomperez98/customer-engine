"""Automatic responses core."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Self
from uuid import UUID

import orjson
from mashumaro.mixins.orjson import DataClassORJSONMixin

from customer_engine_api.core.automatic_responses import embeddings
from customer_engine_api.core.interfaces import SqlQueriable

if TYPE_CHECKING:
    from sqlalchemy import Row

__all__ = ["embeddings"]


@dataclass(frozen=False)
class AutomaticResponse(DataClassORJSONMixin, SqlQueriable):
    """Automatic response."""

    org_code: str
    automatic_response_id: UUID
    name: str
    examples: list[str]
    embedding_model: embeddings.EmbeddingModels
    response: str

    @classmethod
    def from_row(cls: type[Self], row: Row[Any]) -> Self:
        """Instantiate from row."""
        row_data = row._asdict()
        row_data["examples"] = orjson.loads(row_data["examples"])
        return cls.from_dict(row_data)
