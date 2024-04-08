"""Register whatsapp tokens."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import lego_workflows
import sqlalchemy
from lego_workflows.components import (
    CommandComponent,
    DomainError,
    DomainEvent,
    ResponseComponent,
)
from sqlalchemy import bindparam, text

from customer_engine_api.core import whatsapp
from customer_engine_api.core.config import resources
from customer_engine_api.core.logging import logger
from customer_engine_api.handlers.whatsapp import get_tokens

if TYPE_CHECKING:
    from sqlalchemy import Connection


@dataclass(frozen=True)
class WhatsappTokenRegistered(DomainEvent):
    org_code: str

    async def publish(self) -> None:
        logger.info("Whatsapp token registered for org {org}", org=self.org_code)


class WhatsappTokenAlreadyExistsError(DomainError):
    def __init__(self, org_code: str) -> None:
        super().__init__(f"Whatsapp token data already exists for org {org_code}.")


@dataclass(frozen=True)
class Response(ResponseComponent):
    token: whatsapp.WhatsappTokens


@dataclass(frozen=True)
class Command(CommandComponent[Response]):
    org_code: str
    access_token: str
    user_token: str
    sql_conn: Connection

    def _register_new(self, events: list[DomainEvent]) -> Response:
        whatsapp_token = whatsapp.WhatsappTokens(
            org_code=self.org_code,
            access_token=resources.fernet.encrypt(
                data=self.access_token.encode()
            ).decode(),
            user_token=whatsapp.hashing.hash_string(
                string=self.user_token, algo="sha256"
            ),
        )
        stmt = text(
            """
            INSERT INTO whatsapp_tokens (
            org_code,
            access_token,
            user_token
            ) VALUES (
            :org_code,
            :access_token,
            :user_token
            )
            """
        ).bindparams(
            bindparam(
                key="org_code",
                value=whatsapp_token.org_code,
                type_=sqlalchemy.String(),
            ),
            bindparam(
                key="access_token",
                value=whatsapp_token.access_token,
                type_=sqlalchemy.String(),
            ),
            bindparam(
                key="user_token",
                value=whatsapp_token.user_token,
                type_=sqlalchemy.String(),
            ),
        )
        self.sql_conn.execute(stmt)
        events.append(
            WhatsappTokenRegistered(
                org_code=self.org_code,
            )
        )
        return Response(token=whatsapp_token)

    async def run(self, events: list[DomainEvent]) -> Response:
        try:
            await lego_workflows.run_and_collect_events(
                cmd=get_tokens.Command(org_code=self.org_code, sql_conn=self.sql_conn)
            )
        except get_tokens.WhatsappTokenNotFoundError:
            return self._register_new(events=events)
        raise WhatsappTokenAlreadyExistsError(org_code=self.org_code)
