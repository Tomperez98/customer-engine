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
from customer_engine_api.handlers.automatic_responses import get_auto_res, get_example
from customer_engine_api.handlers.org_settings import get_or_default

if TYPE_CHECKING:
    from uuid import UUID

    import cohere
    from qdrant_client import AsyncQdrantClient


@dataclass(frozen=True)
class ExampleCreated(DomainEvent):  # noqa: D101
    org_code: str
    example_id: UUID

    async def publish(self) -> None:  # noqa: D102
        logger.info(
            "New example created with id {example_id} on org {org_code}",
            example_id=self.example_id,
            org_code=self.org_code,
        )


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
            bindparam(key="example", value=self.example, type_=sqlalchemy.String()),
        )

        self.sql_conn.execute(stmt)

        await self._upsert_example(example_id=example_id)

        events.append(
            ExampleCreated(
                org_code=self.org_code,
                example_id=example_id,
            )
        )
        return Response(example_id=example_id)

    async def _upsert_example(self, example_id: UUID) -> None:
        embedding_model_to_use = (
            await lego_workflows.run_and_collect_events(
                cmd=get_or_default.Command(
                    org_code=self.org_code, sql_conn=self.sql_conn
                )
            )
        )[0].settings.embeddings_model
        return await automatic_responses.embeddings.upsert_example(
            embedding_model=embedding_model_to_use,
            qdrant_client=self.qdrant_client,
            cohere_client=self.cohere_client,
            example_id=example_id,
            example=self.example,
            org_code=self.org_code,
        )
