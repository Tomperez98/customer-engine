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
from qdrant_client.http.models import ExtendedPointId, PointIdsList
from sqlalchemy import Connection, bindparam, text

from customer_engine_api.core.logging import logger

if TYPE_CHECKING:
    from uuid import UUID

    import qdrant_client


@dataclass(frozen=True)
class ExampleDeleted(DomainEvent):
    org_code: str
    example_id: UUID

    async def publish(self) -> None:
        logger.info(
            "Example {example_id} from org {org_code} deleted.",
            example_id=self.example_id,
            org_code=self.org_code,
        )


@dataclass(frozen=True)
class Response(ResponseComponent): ...


@dataclass(frozen=True)
class Command(CommandComponent[Response]):
    org_code: str
    example_ids: list[UUID]
    sql_conn: Connection
    qdrant_client: qdrant_client.AsyncQdrantClient

    async def run(self, events: list[DomainEvent]) -> Response:
        ids_to_delete: list[ExtendedPointId] = [
            example_id.hex for example_id in self.example_ids
        ]
        stmt = text(
            """
            DELETE FROM automatic_response_examples
            WHERE org_code = :org_code
                AND example_id IN :example_ids
            """
        ).bindparams(
            bindparam(key="org_code", value=self.org_code, type_=sqlalchemy.String()),
            bindparam(
                key="example_ids",
                value=ids_to_delete,
                type_=sqlalchemy.ARRAY(sqlalchemy.UUID()),
                expanding=True,
            ),
        )

        self.sql_conn.execute(stmt)

        if len(ids_to_delete) > 0:
            await self.qdrant_client.delete(
                collection_name=self.org_code,
                points_selector=PointIdsList(points=ids_to_delete),
            )

        events.extend(
            ExampleDeleted(
                org_code=self.org_code,
                example_id=example_id,
            )
            for example_id in self.example_ids
        )
        return Response()
