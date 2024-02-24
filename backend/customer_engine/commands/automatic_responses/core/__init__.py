"""Automatic responses core."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Self, assert_never
from uuid import UUID

import orjson
from cohere.responses.embeddings import EmbeddingsByType
from mashumaro.mixins.orjson import DataClassORJSONMixin

from customer_engine.commands.automatic_responses.core.typing import EmbeddingModels

if TYPE_CHECKING:
    import cohere
    from sqlalchemy import Row


@dataclass(frozen=False)
class AutomaticResponse(DataClassORJSONMixin):
    """Automatic response."""

    org_code: str
    automatic_response_id: UUID
    name: str
    examples: list[str]
    embedding_model: EmbeddingModels
    response: str

    @classmethod
    def from_row(cls: type[Self], row: Row[Any]) -> Self:
        """Instantiate from row."""
        row_data = row._asdict()
        row_data["examples"] = orjson.loads(row_data["examples"])
        return cls.from_dict(row_data)


async def cohere_embed_examples_and_prompt(
    client: cohere.AsyncClient,
    model: EmbeddingModels,
    examples_or_prompt: list[str] | str,
) -> list[list[float]]:
    """Embed examples and prompt using cohere."""
    provider, model_name = model.split(sep=":", maxsplit=1)
    if provider != "cohere":
        msg = "Model provided is not from cohere."
        raise RuntimeError(msg)
    if isinstance(examples_or_prompt, str):
        examples_or_prompt = [examples_or_prompt]
    elif isinstance(examples_or_prompt, list):
        examples_or_prompt = ["\n".join(examples_or_prompt)]
    else:
        assert_never(examples_or_prompt)

    embeddings = (
        await client.embed(
            model=model_name, input_type="search_document", texts=examples_or_prompt
        )
    ).embeddings

    if isinstance(embeddings, EmbeddingsByType):
        msg = "Unexpected response type from cohere."
        raise TypeError(msg)

    return embeddings
