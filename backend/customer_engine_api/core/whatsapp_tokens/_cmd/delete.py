"""Delete whatsapp token."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import sqlalchemy
from lego_workflows.components import CommandComponent, DomainEvent, ResponseComponent
from sqlalchemy import bindparam, text

from customer_engine_api.logging import logger

if TYPE_CHECKING:
    from sqlalchemy import Connection


@dataclass(frozen=True)
class WhatsappTokensDeleted(DomainEvent):
    org_code: str

    async def publish(self) -> None:
        logger.info(
            "Whatsapp token data deleted for org {org_code}",
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
            DELETE FROM whatsapp_tokens
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
        events.append(WhatsappTokensDeleted(org_code=self.org_code))
        return Response()
