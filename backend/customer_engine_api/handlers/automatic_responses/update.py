"""Update automatic response."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import lego_workflows
import sqlalchemy
from lego_workflows.components import CommandComponent, DomainEvent, ResponseComponent
from sqlalchemy import bindparam, text

from customer_engine_api.handlers.automatic_responses import get

if TYPE_CHECKING:
    from uuid import UUID

    from sqlalchemy import Connection

    from customer_engine_api.core import automatic_responses


@dataclass(frozen=True)
class Response(ResponseComponent):  # noqa: D101
    updated_automatic_response: automatic_responses.AutomaticResponse


@dataclass(frozen=True)
class Command(CommandComponent[Response]):  # noqa: D101
    org_code: str
    automatic_response_id: UUID
    new_name: str | None
    new_response: str | None
    sql_conn: Connection

    async def run(self, events: list[DomainEvent]) -> Response:  # noqa: ARG002, D102
        existing_automatic_response = (
            await lego_workflows.run_and_collect_events(
                cmd=get.Command(
                    org_code=self.org_code,
                    automatic_response_id=self.automatic_response_id,
                    sql_conn=self.sql_conn,
                )
            )
        )[0].automatic_response

        if self.new_name is not None:
            existing_automatic_response.name = self.new_name
        if self.new_response is not None:
            existing_automatic_response.response = self.new_response

        stmt = text(
            """
            UPDATE automatic_responses
            SET
                name = :name,
                response = :response
            WHERE
                org_code = :org_code
                AND automatic_response_id = :automatic_response_id
            """
        ).bindparams(
            bindparam(
                key="org_code",
                value=existing_automatic_response.org_code,
                type_=sqlalchemy.String(),
            ),
            bindparam(
                key="automatic_response_id",
                value=existing_automatic_response.automatic_response_id,
                type_=sqlalchemy.UUID(),
            ),
            bindparam(
                key="name",
                value=existing_automatic_response.name,
                type_=sqlalchemy.String(),
            ),
            bindparam(
                key="response",
                value=existing_automatic_response.response,
                type_=sqlalchemy.String(),
            ),
        )
        self.sql_conn.execute(stmt)

        return Response(
            updated_automatic_response=existing_automatic_response,
        )
