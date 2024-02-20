"""Whatsapp Flows."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, TypeAlias, assert_never, cast
from uuid import UUID

from cohere.responses.embeddings import EmbeddingsByType
from mashumaro.mixins.orjson import DataClassORJSONMixin
from qdrant_client.http.models import Distance

if TYPE_CHECKING:
    import cohere

EmbeddingModels: TypeAlias = Literal["cohere:embed-multilingual-light-v3.0"]
ModelProviders: TypeAlias = Literal["cohere"]


def _split_embedding_model(model: EmbeddingModels) -> tuple[ModelProviders, str]:
    """Split embedding model into components."""
    provider, model_name = model.split(sep=":", maxsplit=1)
    return cast(ModelProviders, provider), model_name


@dataclass(frozen=True)
class _ModelProp(DataClassORJSONMixin):
    size: int
    distance: Distance


def model_props(model: EmbeddingModels) -> _ModelProp:
    """Get props from model."""
    if model == "cohere:embed-multilingual-light-v3.0":
        return _ModelProp(size=384, distance=Distance.COSINE)

    assert_never(model)


async def embed_description_and_prompt(
    cohere: cohere.AsyncClient,
    model: EmbeddingModels,
    examples: list[str],
) -> list[list[float]]:
    """Embed example with provider."""
    provider, model_name = _split_embedding_model(model=model)
    if provider == "cohere":
        embeddings = (
            await cohere.embed(
                model=model_name,
                input_type="search_document",
                texts=["\n".join(examples)],
            )
        ).embeddings
        if isinstance(embeddings, EmbeddingsByType):
            msg = "Unexpected response type."
            raise TypeError(msg)

        return embeddings
    assert_never(provider)


@dataclass(frozen=True)
class UrlForm(DataClassORJSONMixin):
    """Url based forms."""

    url: str


@dataclass(frozen=True)
class WhatsAppFlowForm(DataClassORJSONMixin):
    """Whatsapp flow based forms."""

    flow_id: str


FormConfig: TypeAlias = UrlForm | WhatsAppFlowForm


@dataclass()
class Form(DataClassORJSONMixin):
    """WhatsApp Flow."""

    org_code: str
    form_id: UUID
    name: str
    examples: list[str]
    embedding_model: EmbeddingModels
