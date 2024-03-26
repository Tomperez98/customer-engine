"""Delete example."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import sqlalchemy
from lego_workflows.components import (
    CommandComponent,
    DomainEvent,
    ResponseComponent,
)
from qdrant_client.http.models import PointIdsList
from sqlalchemy import Connection, bindparam, text

from customer_engine_api.core.logging import logger

if TYPE_CHECKING:
    from uuid import UUID

    from qdrant_client import AsyncQdrantClient


@dataclass(frozen=True)
class ExampleDeleted(DomainEvent):  # noqa: D101
    org_code: str
    example_id: UUID

    async def publish(self) -> None:  # noqa: D102
        logger.info(
            "Example {example_id} from org {org_code} deleted.",
            example_id=self.example_id,
            org_code=self.org_code,
        )


@dataclass(frozen=True)
class Response(ResponseComponent): ...  # noqa: D101


@dataclass(frozen=True)
class Command(CommandComponent[Response]):  # noqa: D101
    org_code: str
    example_id: UUID
    sql_conn: Connection
    qdrant_client: AsyncQdrantClient

    async def run(self, events: list[DomainEvent]) -> Response:  # noqa: D102
        stmt = text(
            """
            DELETE FROM automatic_response_examples
            WHERE org_code = :org_code
                AND example_id = :example_id
            """
        ).bindparams(
            bindparam(key="org_code", value=self.org_code, type_=sqlalchemy.String()),
            bindparam(key="example_id", value=self.example_id, type_=sqlalchemy.UUID()),
        )

        self.sql_conn.execute(stmt)

        await self.qdrant_client.delete(
            collection_name=self.org_code,
            points_selector=PointIdsList(points=[self.example_id.hex]),
        )
        events.append(
            ExampleDeleted(
                org_code=self.org_code,
                example_id=self.example_id,
            )
        )
        return Response()
