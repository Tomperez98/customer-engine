"""Whatsapp Flows."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, TypeAlias, assert_never
from uuid import UUID

from cohere.responses.embeddings import EmbeddingsByType
from mashumaro.mixins.orjson import DataClassORJSONMixin
from qdrant_client.http.models import Distance

if TYPE_CHECKING:
    import cohere

CohereModels: TypeAlias = Literal["embed-multilingual-light-v3.0"]


@dataclass(frozen=True)
class _ModelProp:
    size: int
    distance: Distance


def model_props(model: CohereModels) -> _ModelProp:
    """Get props from model."""
    if model == "embed-multilingual-light-v3.0":
        return _ModelProp(size=384, distance=Distance.COSINE)

    assert_never(model)


async def embed_description(
    cohere: cohere.AsyncClient, model: CohereModels, description: str
) -> list[list[float]]:
    """Embed description with cohere."""
    embeddings = (
        await cohere.embed(
            model=model, input_type="search_document", texts=[description]
        )
    ).embeddings
    if isinstance(embeddings, EmbeddingsByType):
        msg = "Unexpected response type."
        raise TypeError(msg)

    return embeddings


@dataclass()
class WhatsAppFlow(DataClassORJSONMixin):
    """WhatsApp Flow."""

    org_code: str
    flow_id: UUID
    name: str
    description: str
    embedding_model: CohereModels
