"""Embeddings."""

from __future__ import annotations

from typing import TYPE_CHECKING

from cohere.responses.embeddings import EmbeddingsByType

if TYPE_CHECKING:
    import cohere

    from customer_engine_api.core.typing import EmbeddingModels


async def embed_prompt(
    client: cohere.AsyncClient,
    model: EmbeddingModels,
    prompt: str,
) -> list[list[float]]:
    """Embed examples and prompt using cohere."""
    provider, model_name = model.split(sep=":", maxsplit=1)
    if provider != "cohere":
        msg = "Model provided is not from cohere."
        raise RuntimeError(msg)

    embeddings = (
        await client.embed(
            model=model_name, input_type="search_document", texts=[prompt]
        )
    ).embeddings

    if isinstance(embeddings, EmbeddingsByType):
        msg = "Unexpected response type from cohere."
        raise TypeError(msg)

    return embeddings
