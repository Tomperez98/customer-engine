"""List example automatic response."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import sqlalchemy
from lego_workflows.components import CommandComponent, DomainEvent, ResponseComponent
from sqlalchemy import Connection, bindparam, text

from customer_engine_api.core.automatic_responses import Example

if TYPE_CHECKING:
    from uuid import UUID


@dataclass(frozen=True)
class Response(ResponseComponent):  # noqa: D101
    examples: list[Example]


@dataclass(frozen=True)
class Command(CommandComponent[Response]):  # noqa: D101
    org_code: str
    automatic_response_id: UUID
    sql_conn: Connection

    async def run(self, events: list[DomainEvent]) -> Response:  # noqa: ARG002, D102
        stmt = text(
            """
            SELECT
                org_code,
                automatic_response_id,
                example_id,
                example
            FROM automatic_response_examples
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

        return Response(
            examples=[
                Example.from_row(row) for row in self.sql_conn.execute(stmt).fetchall()
            ]
        )
