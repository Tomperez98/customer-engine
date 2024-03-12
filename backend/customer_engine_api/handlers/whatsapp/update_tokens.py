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

from customer_engine_api.core import whatsapp
from customer_engine_api.core.config import resources
from customer_engine_api.core.logging import logger
from customer_engine_api.handlers.whatsapp import get_tokens


@dataclass(frozen=True)
class WhatsappTokenUpdated(DomainEvent):  # noqa: D101
    org_code: str

    async def publish(self) -> None:  # noqa: D102
        logger.info(
            "Whatsapp token data updated for org {org_code}",
            org_code=self.org_code,
        )


@dataclass(frozen=True)
class Response(ResponseComponent): ...  # noqa: D101


@dataclass(frozen=True)
class Command(CommandComponent[Response]):  # noqa: D101
    org_code: str
    new_access_token: str | None
    new_user_token: str | None
    sql_conn: Connection

    async def run(self, events: list[DomainEvent]) -> Response:  # noqa: D102
        existing_whatsapp_token = (
            await lego_workflows.run_and_collect_events(
                cmd=get_tokens.Command(org_code=self.org_code, sql_conn=self.sql_conn)
            )
        )[0].whatsapp_token

        if self.new_access_token is not None:
            existing_whatsapp_token.access_token = resources.fernet.encrypt(
                self.new_access_token.encode()
            ).decode()
        if self.new_user_token is not None:
            existing_whatsapp_token.user_token = whatsapp.hashing.hash_string(
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
