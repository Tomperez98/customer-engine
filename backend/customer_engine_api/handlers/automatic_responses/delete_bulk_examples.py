"""Delete bulk examples."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import sqlalchemy
from lego_workflows.components import (
    CommandComponent,
    DomainEvent,
    ResponseComponent,
)
from sqlalchemy import Connection, bindparam, text

from customer_engine_api.core.logging import logger

if TYPE_CHECKING:
    from uuid import UUID


@dataclass(frozen=True)
class ExampleDeleted(DomainEvent):  # noqa: D101
    org_code: str
    automatic_response_id: UUID
    example_id: UUID

    async def publish(self) -> None:  # noqa: D102
        logger.info(
            "Example {example_id} from automatic response {automatic_response_id} on org {org_code} deleted.",
            example_id=self.example_id,
            automatic_response_id=self.automatic_response_id,
            org_code=self.org_code,
        )


@dataclass(frozen=True)
class Response(ResponseComponent): ...  # noqa: D101


@dataclass(frozen=True)
class Command(CommandComponent[Response]):  # noqa: D101
    org_code: str
    automatic_response_id: UUID
    example_ids: list[UUID]
    sql_conn: Connection

    async def run(self, events: list[DomainEvent]) -> Response:  # noqa: D102
        stmt = text(
            """
            DELETE FROM automatic_response_examples
            WHERE org_code = :org_code
                AND automatic_response_id = :automatic_response_id
                AND example_id IN :example_ids
            """
        ).bindparams(
            bindparam(key="org_code", value=self.org_code, type_=sqlalchemy.String()),
            bindparam(
                key="automatic_response_id",
                value=self.automatic_response_id,
                type_=sqlalchemy.UUID(),
            ),
            bindparam(
                key="example_ids",
                value=[example_id.hex for example_id in self.example_ids],
                type_=sqlalchemy.ARRAY(sqlalchemy.UUID()),
                expanding=True,
            ),
        )

        self.sql_conn.execute(stmt)

        events.extend(
            ExampleDeleted(
                org_code=self.org_code,
                automatic_response_id=self.automatic_response_id,
                example_id=example_id,
            )
            for example_id in self.example_ids
        )
        return Response()
