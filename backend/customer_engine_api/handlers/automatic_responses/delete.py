"""Delete automatic response."""

from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import TYPE_CHECKING

import sqlalchemy
from lego_workflows.components import CommandComponent, DomainEvent, ResponseComponent
from sqlalchemy import Connection, bindparam, text

from customer_engine_api.core.logging import logger

if TYPE_CHECKING:
    from uuid import UUID


@dataclass(frozen=True)
class AutomaticResponseDeleted(DomainEvent):
    """Indicated that an automatic response has been deleted."""

    org_code: str
    automatic_response_id: UUID
    deleted_at: datetime.datetime

    async def publish(self) -> None:  # noqa: D102
        logger.info(
            "Automatic response with ID {automatic_response_id} from organization {org_code} has been deleted at {deleted_at}",
            automatic_response_id=self.automatic_response_id,
            org_code=self.org_code,
            deleted_at=self.deleted_at,
        )


@dataclass(frozen=True)
class Response(ResponseComponent):  # noqa: D101
    automatic_response_id: UUID


@dataclass(frozen=True)
class Command(CommandComponent[Response]):  # noqa: D101
    org_code: str
    automatic_response_id: UUID
    sql_conn: Connection

    async def run(self, events: list[DomainEvent]) -> Response:  # noqa: D102
        stmt = text(
            """
            DELETE FROM automatic_responses
            WHERE org_code = :org_code
                AND automatic_response_id = :automatic_response_id
            """
        ).bindparams(
            bindparam(key="org_code", value=self.org_code, type_=sqlalchemy.String()),
            bindparam(
                key="automatic_response_id",
                value=self.automatic_response_id,
                type_=sqlalchemy.UUID(),
            ),
        )

        self.sql_conn.execute(stmt)

        events.append(
            AutomaticResponseDeleted(
                org_code=self.org_code,
                automatic_response_id=self.automatic_response_id,
                deleted_at=datetime.datetime.now(tz=datetime.UTC),
            )
        )
        return Response(automatic_response_id=self.automatic_response_id)
