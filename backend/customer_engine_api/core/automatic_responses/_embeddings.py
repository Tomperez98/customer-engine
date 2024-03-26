"""Embeddings."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypeAlias, assert_never

from cohere.responses.embeddings import EmbeddingsByType

if TYPE_CHECKING:
    import cohere


EmbeddingModels: TypeAlias = Literal["cohere:embed-multilingual-light-v3.0"]


async def embed_examples_and_prompt(
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
