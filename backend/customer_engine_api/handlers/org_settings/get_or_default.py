"""Get org settings."""

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
from customer_engine_api.core.org_settings import OrgSettings


@dataclass(frozen=True)
class Response(ResponseComponent):  # noqa: D101
    settings: OrgSettings
    is_default: bool


@dataclass(frozen=True)
class Command(CommandComponent[Response]):  # noqa: D101
    org_code: str
    sql_conn: Connection

    async def run(self, events: list[DomainEvent]) -> Response:  # noqa: ARG002, D102
        stmt = text(
            """
            SELECT
                org_code,
                default_response
            FROM org_settings
            WHERE org_code = :org_code
            """
        ).bindparams(
            bindparam(
                key="org_code",
                value=self.org_code,
                type_=sqlalchemy.String(),
            )
        )

        row = self.sql_conn.execute(stmt).fetchone()
        logger.info(row)
        if row is None:
            return Response(
                settings=OrgSettings(org_code=self.org_code),
                is_default=True,
            )

        return Response(
            settings=OrgSettings.from_row(row=row),
            is_default=False,
        )
