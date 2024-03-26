"""Get automatic response example."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import sqlalchemy
from lego_workflows.components import (
    CommandComponent,
    DomainError,
    DomainEvent,
    ResponseComponent,
)
from sqlalchemy import Connection, bindparam, text

from customer_engine_api.core.automatic_responses import Example

if TYPE_CHECKING:
    from uuid import UUID


class ExampleNotFoundError(DomainError):
    """Raised whan an example does not exists."""

    def __init__(  # noqa: D107
        self,
        org_code: str,
        automatic_response_id: UUID,
        example_id: UUID,
    ) -> None:
        super().__init__(
            f"Example {example_id} for automatic response {automatic_response_id} of org {org_code} not found."
        )


@dataclass(frozen=True)
class Response(ResponseComponent):
    """Response data for getting an automatic response example."""

    example: Example


@dataclass(frozen=True)
class Command(CommandComponent[Response]):  # noqa: D101
    org_code: str
    automatic_response_id: UUID
    example_id: UUID
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
                AND example_id = :example_id
            """
        ).bindparams(
            bindparam(key="org_code", value=self.org_code, type_=sqlalchemy.String()),
            bindparam(
                key="automatic_response_id",
                value=self.automatic_response_id,
                type_=sqlalchemy.UUID(),
            ),
            bindparam(key="example_id", value=self.example_id, type_=sqlalchemy.UUID()),
        )

        row = self.sql_conn.execute(stmt).fetchone()
        if row is None:
            raise ExampleNotFoundError(
                org_code=self.org_code,
                automatic_response_id=self.automatic_response_id,
                example_id=self.example_id,
            )

        return Response(example=Example.from_row(row=row))
