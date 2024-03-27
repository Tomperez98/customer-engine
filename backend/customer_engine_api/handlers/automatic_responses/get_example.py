"""Get automatic response example."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import lego_workflows
import sqlalchemy
from lego_workflows.components import (
    CommandComponent,
    DomainError,
    DomainEvent,
    ResponseComponent,
)
from sqlalchemy import Connection, bindparam, text

from customer_engine_api.core.automatic_responses import Example
from customer_engine_api.handlers.automatic_responses import get_auto_res

if TYPE_CHECKING:
    from uuid import UUID


class ExampleNotFoundError(DomainError):
    """Raised whan an example does not exists."""

    def __init__(  # noqa: D107
        self,
        org_code: str,
        example_id: UUID,
    ) -> None:
        super().__init__(f"Example {example_id} from org {org_code} not found.")


@dataclass(frozen=True)
class Response(ResponseComponent):
    """Response data for getting an automatic response example."""

    example: Example


@dataclass(frozen=True)
class Command(CommandComponent[Response]):  # noqa: D101
    org_code: str
    automatic_response_id: UUID | None
    example_id: UUID
    sql_conn: Connection

    async def run(self, events: list[DomainEvent]) -> Response:  # noqa: ARG002, D102
        if self.automatic_response_id is not None:
            await lego_workflows.run_and_collect_events(
                cmd=get_auto_res.Command(
                    org_code=self.org_code,
                    automatic_response_id=self.automatic_response_id,
                    sql_conn=self.sql_conn,
                )
            )
        stmt = text(
            """
            SELECT
                org_code,
                automatic_response_id,
                example_id,
                example
            FROM automatic_response_examples
            WHERE org_code = :org_code
                AND example_id = :example_id
            """
        ).bindparams(
            bindparam(key="org_code", value=self.org_code, type_=sqlalchemy.String()),
            bindparam(key="example_id", value=self.example_id, type_=sqlalchemy.UUID()),
        )

        row = self.sql_conn.execute(stmt).fetchone()
        if row is None:
            raise ExampleNotFoundError(
                org_code=self.org_code,
                example_id=self.example_id,
            )

        return Response(example=Example.from_row(row=row))
