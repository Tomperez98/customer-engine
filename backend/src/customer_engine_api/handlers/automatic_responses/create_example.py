"""Create automatic response example."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import uuid4

import lego_workflows
import sqlalchemy
from lego_workflows.components import CommandComponent, DomainEvent, ResponseComponent
from sqlalchemy import Connection, bindparam, text

from customer_engine_api.core import automatic_responses
from customer_engine_api.core.logging import logger
from customer_engine_api.handlers.automatic_responses import (
    create_qdrant_collection,
    get_auto_res,
    get_example,
)
from customer_engine_api.handlers.org_settings import get_or_default

if TYPE_CHECKING:
    from uuid import UUID

    import cohere
    from qdrant_client import AsyncQdrantClient


@dataclass(frozen=True)
class ExampleCreated(DomainEvent):
    org_code: str
    example_id: UUID

    async def publish(self) -> None:
        logger.info(
            "New example created with id {example_id} on org {org_code}",
            example_id=self.example_id,
            org_code=self.org_code,
        )


@dataclass(frozen=True)
class Response(ResponseComponent):
    example_ids: list[UUID]


@dataclass(frozen=True)
class Command(CommandComponent[Response]):
    org_code: str
    examples: list[str]
    automatic_response_id: UUID
    qdrant_client: AsyncQdrantClient
    cohere_client: cohere.AsyncClient
    sql_conn: Connection

    async def _create_example(self, events: list[DomainEvent], example: str) -> UUID:
        while True:
            example_id = uuid4()
            try:
                await lego_workflows.run_and_collect_events(
                    get_example.Command(
                        org_code=self.org_code,
                        example_id=example_id,
                        sql_conn=self.sql_conn,
                        automatic_response_id=self.automatic_response_id,
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
            bindparam(key="example", value=example, type_=sqlalchemy.String()),
        )

        self.sql_conn.execute(stmt)

        events.append(
            ExampleCreated(
                org_code=self.org_code,
                example_id=example_id,
            )
        )

        return example_id

    async def run(self, events: list[DomainEvent]) -> Response:
        await lego_workflows.run_and_collect_events(
            cmd=get_auto_res.Command(
                org_code=self.org_code,
                automatic_response_id=self.automatic_response_id,
                sql_conn=self.sql_conn,
            )
        )
        example_ids: list[UUID] = []
        for example in self.examples:
            example_id = await self._create_example(events=events, example=example)
            example_ids.append(example_id)

        await self._upsert_example(example_ids=example_ids, events=events)
        return Response(example_ids=example_ids)

    async def _upsert_example(
        self, example_ids: list[UUID], events: list[DomainEvent]
    ) -> None:
        embedding_model_to_use = (
            await lego_workflows.run_and_collect_events(
                cmd=get_or_default.Command(
                    org_code=self.org_code, sql_conn=self.sql_conn
                )
            )
        )[0].settings.embeddings_model

        if not (
            await self.qdrant_client.collection_exists(collection_name=self.org_code)
        ):
            (
                _,
                create_qdrant_collection_events,
            ) = await lego_workflows.run_and_collect_events(
                cmd=create_qdrant_collection.Command(
                    org_code=self.org_code,
                    qdrant_client=self.qdrant_client,
                    embedding_model=embedding_model_to_use,
                )
            )
            events.extend(create_qdrant_collection_events)

        return await automatic_responses.embeddings.upsert_examples(
            embedding_model=embedding_model_to_use,
            qdrant_client=self.qdrant_client,
            cohere_client=self.cohere_client,
            example_ids=example_ids,
            examples=self.examples,
            org_code=self.org_code,
        )
