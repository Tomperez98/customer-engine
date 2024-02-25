"""List automatic responses."""
from __future__ import annotations

from dataclasses import dataclass

import sqlalchemy
from lego_workflows.components import CommandComponent, DomainEvent, ResponseComponent
from sqlalchemy import Connection, bindparam, text

from customer_engine.core.automatic_responses.shared import (
    AutomaticResponse,
)


@dataclass(frozen=True)
class Response(ResponseComponent):  # noqa: D101
    automatic_responses: list[AutomaticResponse]


@dataclass(frozen=True)
class Command(CommandComponent[Response]):  # noqa: D101
    org_code: str
    sql_conn: Connection

    async def run(self, events: list[DomainEvent]) -> Response:  # noqa: ARG002, D102
        stmt = text(
            """
            SELECT
                org_code,
                automatic_response_id,
                name,
                examples,
                embedding_model,
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
