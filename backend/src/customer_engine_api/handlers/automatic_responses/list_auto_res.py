"""List automatic responses."""

from __future__ import annotations

from dataclasses import dataclass

import sqlalchemy
from lego_workflows.components import CommandComponent, DomainEvent, ResponseComponent
from sqlalchemy import Connection, bindparam, text

from customer_engine_api.core.automatic_responses import AutomaticResponse


@dataclass(frozen=True)
class Response(ResponseComponent):
    automatic_responses: list[AutomaticResponse]


@dataclass(frozen=True)
class Command(CommandComponent[Response]):
    org_code: str
    sql_conn: Connection

    async def run(self, events: list[DomainEvent]) -> Response:  # noqa: ARG002
        stmt = text(
            """
            SELECT
                org_code,
                automatic_response_id,
                name,
                response
            FROM automatic_responses
            WHERE org_code = :org_code
            """
        ).bindparams(
            bindparam(key="org_code", value=self.org_code, type_=sqlalchemy.String())
        )

        return Response(
            automatic_responses=[
                AutomaticResponse.from_row(row)
                for row in self.sql_conn.execute(statement=stmt).fetchall()
            ]
        )
