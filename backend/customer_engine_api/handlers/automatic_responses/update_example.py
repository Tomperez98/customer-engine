"""Update example."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import lego_workflows
import sqlalchemy
from lego_workflows.components import CommandComponent, DomainEvent, ResponseComponent
from sqlalchemy import Connection, bindparam, text

from customer_engine_api.core import automatic_responses
from customer_engine_api.core.logging import logger
from customer_engine_api.handlers.automatic_responses import get_example
from customer_engine_api.handlers.org_settings import get_or_default

if TYPE_CHECKING:
    from uuid import UUID

    import cohere
    from qdrant_client import AsyncQdrantClient

    from customer_engine_api.core.automatic_responses import Example


@dataclass(frozen=True)
class ExampleUpdated(DomainEvent):  # noqa: D101
    org_code: str
    example_id: UUID

    async def publish(self) -> None:  # noqa: D102
        logger.info(
            "Example {example_id} from org {org_code} has been updated",
            example_id=self.example_id,
            org_code=self.org_code,
        )


@dataclass(frozen=True)
class Response(ResponseComponent):  # noqa: D101
    example: Example


@dataclass(frozen=True)
class Command(CommandComponent[Response]):  # noqa: D101
    org_code: str
    automatic_response_id: UUID
    example_id: UUID
    example: str | None
    sql_conn: Connection
    qdrant_client: AsyncQdrantClient
    cohere_client: cohere.AsyncClient

    async def run(self, events: list[DomainEvent]) -> Response:  # noqa: D102
        response_get_example, _ = await lego_workflows.run_and_collect_events(
            cmd=get_example.Command(
                self.org_code,
                automatic_response_id=self.automatic_response_id,
                example_id=self.example_id,
                sql_conn=self.sql_conn,
            )
        )

        example = response_get_example.example.update(example=self.example)

        stmt = text(
            """
            UPDATE automatic_response_examples
            SET
                example = :example
            WHERE org_code = :org_code
                AND example_id = :example_id
            """
        ).bindparams(
            bindparam(
                key="org_code",
                value=example.org_code,
                type_=sqlalchemy.String(),
            ),
            bindparam(
                key="example_id",
                value=example.example_id,
                type_=sqlalchemy.UUID(),
            ),
            bindparam(
                key="example",
                value=example.example,
                type_=sqlalchemy.String(),
            ),
        )

        self.sql_conn.execute(stmt)

        embedding_model_to_use = (
            await lego_workflows.run_and_collect_events(
                cmd=get_or_default.Command(
                    org_code=self.org_code, sql_conn=self.sql_conn
                )
            )
        )[0].settings.embeddings_model

        await automatic_responses.embeddings.upsert_example(
            embedding_model=embedding_model_to_use,
            cohere_client=self.cohere_client,
            qdrant_client=self.qdrant_client,
            example_id=example.example_id,
            example=example.example,
            org_code=example.org_code,
        )
        events.append(
            ExampleUpdated(
                org_code=example.org_code,
                example_id=example.example_id,
            )
        )
        return Response(example=example)
