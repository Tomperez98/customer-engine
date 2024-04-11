"""Create qdrant collection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from lego_workflows.components import CommandComponent, DomainEvent, ResponseComponent

from customer_engine_api.core import automatic_responses
from customer_engine_api.core.logging import logger

if TYPE_CHECKING:
    from qdrant_client import AsyncQdrantClient

    from customer_engine_api.core.typing import EmbeddingModels


@dataclass(frozen=True)
class QdrantCollectionCreated(DomainEvent):
    org_code: str
    embedding_model: EmbeddingModels

    async def publish(self) -> None:
        logger.info(
            "Qdrant collection for org {org_code} created with model {model}",
            org_code=self.org_code,
            model=self.embedding_model,
        )


@dataclass(frozen=True)
class Response(ResponseComponent): ...


@dataclass(frozen=True)
class Command(CommandComponent[Response]):
    org_code: str
    qdrant_client: AsyncQdrantClient
    embedding_model: EmbeddingModels

    async def run(self, events: list[DomainEvent]) -> Response:
        await self.qdrant_client.create_collection(
            collection_name=self.org_code,
            vectors_config=automatic_responses.embeddings.qdrant_vector_params_per_model(
                model=self.embedding_model
            ),
        )
        events.append(
            QdrantCollectionCreated(
                org_code=self.org_code, embedding_model=self.embedding_model
            )
        )
        return Response()
