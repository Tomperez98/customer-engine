"""Get automatic response."""
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

from customer_engine_api.core.automatic_responses import core

if TYPE_CHECKING:
    from uuid import UUID


class AutomaticResponseNotFoundError(DomainError):
    """Raised when automatic response does not exists in database."""

    def __init__(self, org_code: str, automatic_response_id: UUID) -> None:
        super().__init__(
            f"Automatic response not found for {org_code} with ID {automatic_response_id}"
        )


@dataclass(frozen=True)
class Response(ResponseComponent):
    """Response data for getting an automatic response."""

    automatic_response: core.AutomaticResponse


@dataclass(frozen=True)
class Command(CommandComponent[Response]):
    org_code: str
    automatic_response_id: UUID
    sql_conn: Connection

    async def run(self, events: list[DomainEvent]) -> Response:  # noqa: ARG002
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

        automatic_response_row = self.sql_conn.execute(stmt).fetchone()
        if automatic_response_row is None:
            raise AutomaticResponseNotFoundError(
                org_code=self.org_code, automatic_response_id=self.automatic_response_id
            )

        return Response(
            automatic_response=core.AutomaticResponse.from_row(automatic_response_row)
        )
