"""Embeddings."""

from __future__ import annotations

from typing import TYPE_CHECKING

from cohere.responses.embeddings import EmbeddingsByType
from qdrant_client.http.models import (
    Batch,
    UpdateStatus,
)

if TYPE_CHECKING:
    from uuid import UUID

    import cohere
    from qdrant_client import AsyncQdrantClient

    from customer_engine_api.core.typing import EmbeddingModels


async def embed_prompt_or_examples(
    client: cohere.AsyncClient,
    model: EmbeddingModels,
    prompt_or_examples: str | list[str],
) -> list[list[float]]:
    """Embed examples and prompt using cohere."""
    provider, model_name = model.split(sep=":", maxsplit=1)
    if provider != "cohere":
        msg = "Model provided is not from cohere."
        raise RuntimeError(msg)

    if isinstance(prompt_or_examples, str):
        prompt_or_examples = [prompt_or_examples]

    embeddings: list[list[float]] | EmbeddingsByType = (
        await client.embed(
            model=model_name,
            input_type="search_document",
            texts=prompt_or_examples,
        )
    ).embeddings

    if isinstance(embeddings, EmbeddingsByType):
        msg = "Unexpected response type from cohere."
        raise TypeError(msg)

    return embeddings


async def upsert_examples(  # noqa: PLR0913
    *,
    embedding_model: EmbeddingModels,
    qdrant_client: AsyncQdrantClient,
    cohere_client: cohere.AsyncClient,
    example_ids: list[UUID],
    examples: list[str],
    org_code: str,
) -> None:
    """Upsert example embeddings into qdrant database."""
    if len(example_ids) != len(examples):
        msg = "Len of example ids and len of example must be equal"
        raise ValueError(msg)

    example_embeddings = await embed_prompt_or_examples(
        client=cohere_client, model=embedding_model, prompt_or_examples=examples
    )
    upsert_result = await qdrant_client.upsert(
        collection_name=org_code,
        points=Batch(
            ids=[example_id.hex for example_id in example_ids],
            vectors=example_embeddings,
        ),
    )

    if upsert_result.status == UpdateStatus.ACKNOWLEDGED:
        msg = "Upsert should have been complited."
        raise TypeError(msg)
