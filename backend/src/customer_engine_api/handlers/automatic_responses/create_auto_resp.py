"""Create automatic response."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import uuid4

import lego_workflows
import sqlalchemy
from lego_workflows.components import CommandComponent, DomainEvent, ResponseComponent
from sqlalchemy import bindparam, text

from customer_engine_api.core.logging import logger
from customer_engine_api.handlers.automatic_responses import (
    create_example,
    get_auto_res,
)

if TYPE_CHECKING:
    from uuid import UUID

    import cohere
    from qdrant_client import AsyncQdrantClient
    from sqlalchemy import Connection


@dataclass(frozen=True)
class AutomaticResponseCreated(DomainEvent):
    """Notifies when new automatic response has been created."""

    org_code: str
    automatic_response_id: UUID

    async def publish(self) -> None:
        logger.info(
            "New automatic response with ID {automatic_response_id} for organization {org_code} has been created.",
            automatic_response_id=self.automatic_response_id,
            org_code=self.org_code,
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
    response: str
    examples: list[str] | None
    qdrant_client: AsyncQdrantClient
    cohere_client: cohere.AsyncClient
    sql_conn: Connection

    async def run(self, events: list[DomainEvent]) -> Response:
        """Command execution."""
        while True:
            random_id = uuid4()
            try:
                await lego_workflows.run_and_collect_events(
                    get_auto_res.Command(
                        org_code=self.org_code,
                        automatic_response_id=random_id,
                        sql_conn=self.sql_conn,
                    )
                )
            except get_auto_res.AutomaticResponseNotFoundError:
                break
        stmt = text(
            """
            INSERT INTO automatic_responses (
            org_code,
            automatic_response_id,
            name,
            response
            ) VALUES (
            :org_code,
            :automatic_response_id,
            :name,
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
            bindparam(key="response", value=self.response, type_=sqlalchemy.String()),
        )

        self.sql_conn.execute(stmt)

        events.append(
            AutomaticResponseCreated(
                org_code=self.org_code, automatic_response_id=random_id
            )
        )
        if self.examples is not None:
            (
                _,
                examples_created_events,
            ) = await lego_workflows.run_and_collect_events(
                create_example.Command(
                    org_code=self.org_code,
                    examples=self.examples,
                    automatic_response_id=random_id,
                    qdrant_client=self.qdrant_client,
                    cohere_client=self.cohere_client,
                    sql_conn=self.sql_conn,
                )
            )
            events.extend(examples_created_events)

        return Response(automatic_response_id=random_id)
