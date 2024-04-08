"""Delete org settings."""

from __future__ import annotations

from dataclasses import dataclass

import sqlalchemy
from lego_workflows.components import (
    CommandComponent,
    DomainEvent,
    ResponseComponent,
)
from sqlalchemy import Connection, bindparam, text

from customer_engine_api.core.logging import logger


@dataclass(frozen=True)
class OrgSettingsDeleted(DomainEvent):
    org_code: str

    async def publish(self) -> None:
        logger.info(
            "Org settings deleted for organization {org_code}",
            org_code=self.org_code,
        )


@dataclass(frozen=True)
class Response(ResponseComponent): ...


@dataclass(frozen=True)
class Command(CommandComponent[Response]):
    org_code: str
    sql_conn: Connection

    async def run(self, events: list[DomainEvent]) -> Response:
        stmt = text(
            """
            DELETE FROM org_settings
            WHERE org_code = :org_code
            """
        ).bindparams(
            bindparam(
                key="org_code",
                value=self.org_code,
                type_=sqlalchemy.String(),
            )
        )
        self.sql_conn.execute(stmt)
        events.append(OrgSettingsDeleted(org_code=self.org_code))
        return Response()
