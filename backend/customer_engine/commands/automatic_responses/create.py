"""Create automatic response."""
from __future__ import annotations

import contextlib
from dataclasses import dataclass
from typing import TYPE_CHECKING, assert_never
from uuid import uuid4

import lego_workflows
import sqlalchemy
from lego_workflows.components import CommandComponent, DomainEvent, ResponseComponent
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.http.models import Batch, Distance, VectorParams
from sqlalchemy import bindparam, text

from customer_engine import logger
from customer_engine.commands.automatic_responses import get
from customer_engine.commands.automatic_responses.core import (
    cohere_embed_examples_and_prompt,
)
from customer_engine.commands.automatic_responses.core.constants import (
    DEFAULT_EMBEDDING_MODEL,
)

if TYPE_CHECKING:
    import datetime
    from uuid import UUID

    import cohere
    from qdrant_client import AsyncQdrantClient
    from sqlalchemy import Connection

    from customer_engine.commands.automatic_responses.core.typing import EmbeddingModels


def _qdrant_vectored_params_per_model(model: EmbeddingModels) -> VectorParams:
    if model == "cohere:embed-multilingual-light-v3.0":
        return VectorParams(size=384, distance=Distance.COSINE)
    assert_never(model)


@dataclass(frozen=True)
class AutomaticResponseCreated(DomainEvent):
    """Notifies when new automatic response has been created."""

    org_code: str
    automatic_response_id: UUID
    created_at: datetime.datetime

    async def publish(self) -> None:  # noqa: D102
        logger.info(
            "New automatic response with ID %s for organization %s has been created at %s.",
            self.automatic_response_id,
            self.org_code,
            self.created_at,
        )


@dataclass(frozen=True)
class Response(ResponseComponent):
    """Response data for command execution."""

    automatic_response_id: UUID


@dataclass(frozen=True)
class Command(CommandComponent[Response]):
    """Input data for command."""

    org_code: str
    name: str
    examples: list[str]
    response: str
    sql_conn: Connection
    qdrant_client: AsyncQdrantClient
    cohere_client: cohere.AsyncClient

    async def run(self, events: list[DomainEvent]) -> Response:  # noqa: ARG002
        """Command execution."""
        embedding_model_to_use = DEFAULT_EMBEDDING_MODEL
        while True:
            random_id = uuid4()
            try:
                await lego_workflows.run_and_collect_events(
                    get.Command(
                        org_code=self.org_code,
                        automatic_response_id=random_id,
                        sql_conn=self.sql_conn,
                    )
                )
            except get.AutomaticResponseNotFoundError:
                break
        stmt = text(
            """
            INSERT INTO automatic_responses (
            org_code,
            automatic_response_id,
            name,
            examples,
            embedding_model,
            response
            ) VALUES (
            :org_code,
            :automatic_response_id,
            :name,
            :examples,
            :embedding_model,
            :response
            )
            """
        ).bindparams(
            bindparam(key="org_code", value=self.org_code, type_=sqlalchemy.String()),
            bindparam(
                key="automatic_response_id",
                value=random_id,
                type_=sqlalchemy.UUID(),
            ),
            bindparam(key="name", value=self.name, type_=sqlalchemy.String()),
            bindparam(key="examples", value=self.examples, type_=sqlalchemy.JSON()),
            bindparam(
                key="embedding_model",
                value=embedding_model_to_use,
                type_=sqlalchemy.String(),
            ),
            bindparam(key="response", value=self.response, type_=sqlalchemy.String()),
        )

        self.sql_conn.execute(stmt)

        collection_created: bool = False
        with contextlib.suppress(UnexpectedResponse):
            collection_created = await self.qdrant_client.create_collection(
                collection_name=self.org_code,
                vectors_config=_qdrant_vectored_params_per_model(
                    model=embedding_model_to_use
                ),
            )
            if not collection_created:
                msg = f"Unable to create collection {self.org_code}"
                raise RuntimeError(msg)

        examples_embeddings = await cohere_embed_examples_and_prompt(
            client=self.cohere_client,
            model=embedding_model_to_use,
            examples_or_prompt=self.examples,
        )

        await self.qdrant_client.upsert(
            collection_name=self.org_code,
            points=Batch(ids=[random_id.hex], vectors=examples_embeddings),
        )

        return Response(automatic_response_id=random_id)
