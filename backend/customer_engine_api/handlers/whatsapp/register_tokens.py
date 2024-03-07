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

from customer_engine_api.config import resources
from customer_engine_api.core.whatsapp import hash_string
from customer_engine_api.handlers.whatsapp import get_tokens
from customer_engine_api.logging import logger

if TYPE_CHECKING:
    from sqlalchemy import Connection


@dataclass(frozen=True)
class WhatsappTokenRegistered(DomainEvent):  # noqa: D101
    org_code: str

    async def publish(self) -> None:  # noqa: D102
        logger.info("Whatsapp token registered for org {org}", org=self.org_code)


class WhatsappTokenAlreadyExistsError(DomainError):  # noqa: D101
    def __init__(self, org_code: str) -> None:  # noqa: D107
        super().__init__(f"Whatsapp token data already exists for org {org_code}.")


@dataclass(frozen=True)
class Response(ResponseComponent): ...  # noqa: D101


@dataclass(frozen=True)
class Command(CommandComponent[Response]):  # noqa: D101
    org_code: str
    access_token: str
    user_token: str
    phone_number_id: int
    sql_conn: Connection

    def _register_new(self, events: list[DomainEvent]) -> Response:
        stmt = text(
            """
            INSERT INTO whatsapp_tokens (
            org_code,
            access_token,
            user_token,
            phone_number_id
            ) VALUES (
            :org_code,
            :access_token,
            :user_token,
            :phone_number_id
            )
            """
        ).bindparams(
            bindparam(
                key="org_code",
                value=self.org_code,
                type_=sqlalchemy.String(),
            ),
            bindparam(
                key="access_token",
                value=resources.fernet.encrypt(
                    data=self.access_token.encode()
                ).decode(),
                type_=sqlalchemy.String(),
            ),
            bindparam(
                key="user_token",
                value=hash_string(string=self.user_token, algo="sha256"),
                type_=sqlalchemy.String(),
            ),
            bindparam(
                "phone_number_id",
                value=self.phone_number_id,
                type_=sqlalchemy.Integer(),
            ),
        )
        self.sql_conn.execute(stmt)
        events.append(
            WhatsappTokenRegistered(
                org_code=self.org_code,
            )
        )
        return Response()

    async def run(self, events: list[DomainEvent]) -> Response:  # noqa: D102
        try:
            await lego_workflows.run_and_collect_events(
                cmd=get_tokens.Command(org_code=self.org_code, sql_conn=self.sql_conn)
            )
        except get_tokens.WhatsappTokenNotFoundError:
            return self._register_new(events=events)
        raise WhatsappTokenAlreadyExistsError(org_code=self.org_code)
