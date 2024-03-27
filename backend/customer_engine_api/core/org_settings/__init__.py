"""Org settings core module."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Self

from mashumaro.mixins.orjson import DataClassORJSONMixin

from customer_engine_api.core.interfaces import SqlQueriable
from customer_engine_api.core.typing import EmbeddingModels

if TYPE_CHECKING:
    from sqlalchemy import Row


@dataclass(frozen=True)
class OrgSettings(DataClassORJSONMixin, SqlQueriable):
    """Org settings."""

    org_code: str
    default_response: str = field(default="No response found for this prompt")
    embeddings_model: EmbeddingModels = field(
        default="cohere:embed-multilingual-light-v3.0"
    )

    @classmethod
    def from_row(cls: type[Self], row: Row[Any]) -> Self:
        """Intialize org settings from row."""
        return cls.from_dict(row._asdict())

    def update(self, default_response: str | None) -> OrgSettings:
        """Update org settings."""
        return OrgSettings(
            org_code=self.org_code,
            default_response=default_response
            if default_response is not None
            else self.default_response,
        )
