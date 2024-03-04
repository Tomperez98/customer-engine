"""Update whatsapp tokens."""

from __future__ import annotations

from dataclasses import dataclass

import lego_workflows
import sqlalchemy
from lego_workflows.components import (
    CommandComponent,
    DomainEvent,
    ResponseComponent,
)
from sqlalchemy import Connection, bindparam, text

from customer_engine_api.config import resources
from customer_engine_api.core.whatsapp_tokens import core
from customer_engine_api.core.whatsapp_tokens._cmd import get
from customer_engine_api.logging import logger


@dataclass(frozen=True)
class WhatsappTokenUpdated(DomainEvent):
    org_code: str

    async def publish(self) -> None:
        logger.info(
            "Whatsapp token data updated for org {org_code}",
            org_code=self.org_code,
        )


@dataclass(frozen=True)
class Response(ResponseComponent): ...


@dataclass(frozen=True)
class Command(CommandComponent[Response]):
    org_code: str
    new_access_token: str | None
    new_user_token: str | None
    sql_conn: Connection

    async def run(self, events: list[DomainEvent]) -> Response:
        existing_whatsapp_token = (
            await lego_workflows.run_and_collect_events(
                cmd=get.Command(org_code=self.org_code, sql_conn=self.sql_conn)
            )
        )[0].whatsapp_token

        if self.new_access_token is not None:
            existing_whatsapp_token.access_token = resources.fernet.encrypt(
                self.new_access_token.encode()
            ).decode()
        if self.new_user_token is not None:
            existing_whatsapp_token.user_token = core.hash_string(
                string=self.new_user_token, algo="sha256"
            )

        stmt = text(
            """
            UPDATE whatsapp_tokens
            SET
                access_token = :access_token,
                user_token = :user_token
            WHERE
                org_code = :org_code
            """
        ).bindparams(
            bindparam(
                key="access_token",
                value=existing_whatsapp_token.access_token,
                type_=sqlalchemy.String(),
            ),
            bindparam(
                key="user_token",
                value=existing_whatsapp_token.user_token,
                type_=sqlalchemy.String(),
            ),
            bindparam(
                key="org_code",
                value=self.org_code,
                type_=sqlalchemy.String(),
            ),
        )
        self.sql_conn.execute(stmt)
        events.append(WhatsappTokenUpdated(org_code=self.org_code))
        return Response()
