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
from customer_engine_api.handlers.automatic_responses import get_auto_res

if TYPE_CHECKING:
    import datetime
    from uuid import UUID

    from sqlalchemy import Connection


@dataclass(frozen=True)
class AutomaticResponseCreated(DomainEvent):
    """Notifies when new automatic response has been created."""

    org_code: str
    automatic_response_id: UUID
    created_at: datetime.datetime

    async def publish(self) -> None:  # noqa: D102
        logger.info(
            "New automatic response with ID {automatic_response_id} for organization {org_code} has been created at {created_at}.",
            automatic_response_id=self.automatic_response_id,
            org_code=self.org_code,
            created_at=self.created_at,
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
    sql_conn: Connection

    async def run(self, events: list[DomainEvent]) -> Response:  # noqa: ARG002
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

        return Response(automatic_response_id=random_id)
