"""Get bulk examples."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import sqlalchemy
from lego_workflows.components import CommandComponent, DomainEvent, ResponseComponent
from sqlalchemy import Connection, bindparam, text

from customer_engine_api.core import automatic_responses

if TYPE_CHECKING:
    from uuid import UUID


@dataclass(frozen=True)
class Response(ResponseComponent):
    examples: list[automatic_responses.Example]


@dataclass(frozen=True)
class Command(CommandComponent[Response]):
    org_code: str
    examples_ids: list[UUID]
    sql_conn: Connection

    async def run(self, events: list[DomainEvent]) -> Response:  # noqa: ARG002
        ids_to_get = (example_id.hex for example_id in self.examples_ids)
        stmt = text(
            """
            SELECT
                org_code,
                automatic_response_id,
                example_id,
                example
            FROM automatic_response_examples
            WHERE org_code = :org_code
                AND example_id IN :example_ids
            """
        ).bindparams(
            bindparam(key="org_code", value=self.org_code, type_=sqlalchemy.String()),
            bindparam(
                key="example_ids",
                value=ids_to_get,
                type_=sqlalchemy.ARRAY(sqlalchemy.UUID()),
                expanding=True,
            ),
        )

        return Response(
            examples=[
                automatic_responses.Example.from_row(row=row)
                for row in self.sql_conn.execute(stmt).fetchall()
            ]
        )
