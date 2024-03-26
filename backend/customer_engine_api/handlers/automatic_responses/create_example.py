"""Create automatic response example."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, assert_never
from uuid import uuid4

import lego_workflows
import sqlalchemy
from lego_workflows.components import CommandComponent, DomainEvent, ResponseComponent
from qdrant_client.http.models import Distance, VectorParams
from sqlalchemy import Connection, bindparam, text

from customer_engine_api.core.logging import logger
from customer_engine_api.handlers.automatic_responses import get_auto_res, get_example

if TYPE_CHECKING:
    from uuid import UUID

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
    automatic_response_id: UUID
    example: str
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
                        automatic_response_id=self.automatic_response_id,
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
        events.append(
            ExampleCreated(
                org_code=self.org_code,
                automatic_response_id=self.automatic_response_id,
                example_id=example_id,
            )
        )
        return Response(example_id=example_id)
