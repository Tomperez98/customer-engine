"""Create automatic response example."""

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
from sqlalchemy import Connection, bindparam, text

from customer_engine_api.core import automatic_responses
from customer_engine_api.core.logging import logger
from customer_engine_api.handlers.automatic_responses import get_auto_res, get_example
from customer_engine_api.handlers.org_settings import get_or_default

if TYPE_CHECKING:
    from uuid import UUID

    import cohere
    from qdrant_client import AsyncQdrantClient

    from customer_engine_api.core.typing import EmbeddingModels


@dataclass(frozen=True)
class ExampleCreated(DomainEvent):  # noqa: D101
    org_code: str
    automatic_response_id: UUID
    example_id: UUID

    async def publish(self) -> None:  # noqa: D102
        logger.info(
            "New example created with id {example_id} for automatic response {automatic_response_id} in org {org_code}",
            example_id=self.example_id,
            automatic_response_id=self.automatic_response_id,
            org_code=self.org_code,
        )


def _qdrant_vectored_params_per_model(model: EmbeddingModels) -> VectorParams:
    if model == "cohere:embed-multilingual-light-v3.0":
        return VectorParams(size=384, distance=Distance.COSINE)
    assert_never(model)


@dataclass(frozen=True)
class Response(ResponseComponent):  # noqa: D101
    example_id: UUID


@dataclass(frozen=True)
class Command(CommandComponent[Response]):  # noqa: D101
    org_code: str
    example: str
    automatic_response_id: UUID
    qdrant_client: AsyncQdrantClient
    cohere_client: cohere.AsyncClient
    sql_conn: Connection

    async def run(self, events: list[DomainEvent]) -> Response:  # noqa: D102
        await lego_workflows.run_and_collect_events(
            cmd=get_auto_res.Command(
                org_code=self.org_code,
                automatic_response_id=self.automatic_response_id,
                sql_conn=self.sql_conn,
            )
        )
        while True:
            example_id = uuid4()
            try:
                await lego_workflows.run_and_collect_events(
                    get_example.Command(
                        org_code=self.org_code,
                        example_id=example_id,
                        sql_conn=self.sql_conn,
                    )
                )
            except get_example.ExampleNotFoundError:
                break

        stmt = text(
            """
            INSERT INTO automatic_response_examples (
                org_code,
                automatic_response_id,
                example_id,
                example
            ) VALUES (
                :org_code,
                :automatic_response_id,
                :example_id,
                :example
            )
            """
        ).bindparams(
            bindparam(key="org_code", value=self.org_code, type_=sqlalchemy.String()),
            bindparam(
                key="automatic_response_id",
                value=self.automatic_response_id,
                type_=sqlalchemy.UUID(),
            ),
            bindparam(key="example_id", value=example_id, type_=sqlalchemy.UUID()),
            bindparam(key="example", value=self.example, type_=sqlalchemy.String()),
        )

        self.sql_conn.execute(stmt)

        embedding_model_to_use = (
            await lego_workflows.run_and_collect_events(
                cmd=get_or_default.Command(
                    org_code=self.org_code, sql_conn=self.sql_conn
                )
            )
        )[0].settings.embeddings_model

        with contextlib.suppress(UnexpectedResponse):
            await self.qdrant_client.create_collection(
                collection_name=self.org_code,
                vectors_config=_qdrant_vectored_params_per_model(
                    model=embedding_model_to_use
                ),
            )
        example_embeddings = await automatic_responses.embeddings.embed_prompt(
            client=self.cohere_client,
            model=embedding_model_to_use,
            prompt=self.example,
        )

        await self.qdrant_client.upsert(
            collection_name=self.org_code,
            points=Batch(
                ids=[example_id.hex],
                vectors=example_embeddings,
            ),
        )
        events.append(
            ExampleCreated(
                org_code=self.org_code,
                automatic_response_id=self.automatic_response_id,
                example_id=example_id,
            )
        )
        return Response(example_id=example_id)
