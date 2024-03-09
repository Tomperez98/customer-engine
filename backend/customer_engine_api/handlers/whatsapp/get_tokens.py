"""Get whatsapp tokens."""

from __future__ import annotations

from dataclasses import dataclass

import sqlalchemy
from lego_workflows.components import (
    CommandComponent,
    DomainError,
    DomainEvent,
    ResponseComponent,
)
from sqlalchemy import Connection, bindparam, text

from customer_engine_api.core.whatsapp import WhatsappTokens


class WhatsappTokenNotFoundError(DomainError):
    """Raised when whatsapp token data is not found."""

    def __init__(self, org_code: str) -> None:  # noqa: D107
        super().__init__(f"Whatsapp Tokens not found for org {org_code}")


@dataclass(frozen=True)
class Response(ResponseComponent):  # noqa: D101
    whatsapp_token: WhatsappTokens


@dataclass(frozen=True)
class Command(CommandComponent[Response]):  # noqa: D101
    org_code: str
    sql_conn: Connection

    async def run(self, events: list[DomainEvent]) -> Response:  # noqa: ARG002, D102
        stmt = text(
            """
                SELECT
                    org_code,
                    access_token,
                    user_token
                FROM whatsapp_tokens
                WHERE org_code = :org_code
            """
        ).bindparams(
            bindparam(key="org_code", value=self.org_code, type_=sqlalchemy.String())
        )
        whatsapp_token_row = self.sql_conn.execute(statement=stmt).one_or_none()
        if whatsapp_token_row is None:
            raise WhatsappTokenNotFoundError(org_code=self.org_code)

        return Response(whatsapp_token=WhatsappTokens.from_row(whatsapp_token_row))
