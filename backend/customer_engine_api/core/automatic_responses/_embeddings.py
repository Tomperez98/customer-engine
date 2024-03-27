"""Embeddings."""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, assert_never

from cohere.responses.embeddings import EmbeddingsByType
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.http.models import (
    Batch,
    Distance,
    UpdateStatus,
    VectorParams,
)

if TYPE_CHECKING:
    from uuid import UUID

    import cohere
    from qdrant_client import AsyncQdrantClient

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


def _qdrant_vectored_params_per_model(model: EmbeddingModels) -> VectorParams:
    if model == "cohere:embed-multilingual-light-v3.0":
        return VectorParams(size=384, distance=Distance.COSINE)
    assert_never(model)


async def upsert_example(  # noqa: PLR0913
    *,
    embedding_model: EmbeddingModels,
    qdrant_client: AsyncQdrantClient,
    cohere_client: cohere.AsyncClient,
    example_id: UUID,
    example: str,
    org_code: str,
) -> None:
    """Upsert example embeddings into qdrant database."""
    with contextlib.suppress(UnexpectedResponse):
        await qdrant_client.create_collection(
            collection_name=org_code,
            vectors_config=_qdrant_vectored_params_per_model(model=embedding_model),
        )

    example_embeddings = await embed_prompt(
        client=cohere_client, model=embedding_model, prompt=example
    )
    upsert_result = await qdrant_client.upsert(
        collection_name=org_code,
        points=Batch(ids=[example_id.hex], vectors=example_embeddings),
    )

    if upsert_result.status == UpdateStatus.ACKNOWLEDGED:
        msg = "Upsert should have been complited."
        raise TypeError(msg)
