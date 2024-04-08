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

from customer_engine_api.core import whatsapp
from customer_engine_api.core.config import resources


class WhatsappTokenNotFoundError(DomainError):
    """Raised when whatsapp token data is not found."""

    def __init__(self, org_code: str) -> None:
        super().__init__(f"Whatsapp Tokens not found for org {org_code}")


@dataclass(frozen=True)
class Response(ResponseComponent):
    whatsapp_token: whatsapp.WhatsappTokens


@dataclass(frozen=True)
class Command(CommandComponent[Response]):
    org_code: str
    sql_conn: Connection

    async def run(self, events: list[DomainEvent]) -> Response:  # noqa: ARG002
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

        whatsapp_tokens: whatsapp.WhatsappTokens = whatsapp.WhatsappTokens.from_row(
            whatsapp_token_row
        ).with_decrypted_access_token(
            fernet=resources.fernet,
        )

        return Response(whatsapp_token=whatsapp_tokens)
