"""Validate token."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from lego_workflows.components import (
    CommandComponent,
    DomainError,
    DomainEvent,
    ResponseComponent,
)

from customer_engine_api.core import jwt
from customer_engine_api.core.logging import logger

if TYPE_CHECKING:
    import datetime

    from fastapi.security import HTTPAuthorizationCredentials


class TokenExpiredError(DomainError):
    """Raised when token has expired."""

    def __init__(self) -> None:  # noqa: D107
        super().__init__("Token expired.")


@dataclass(frozen=True)
class TokenValidated(DomainEvent):  # noqa: D101
    org_code: str

    async def publish(self) -> None:  # noqa: D102
        logger.debug("Token validated for org {org_code}", org_code=self.org_code)


@dataclass(frozen=True)
class Response(ResponseComponent):  # noqa: D101
    org_code: str


@dataclass(frozen=True)
class Command(CommandComponent[Response]):  # noqa: D101
    token: HTTPAuthorizationCredentials
    current_time: datetime.datetime

    async def run(self, events: list[DomainEvent]) -> Response:  # noqa: D102
        decoded_token: jwt.KindeToken = jwt.decode_token(
            encoded_token=self.token.credentials
        )
        if decoded_token.is_expired(current_time=self.current_time):
            raise TokenExpiredError

        events.append(TokenValidated(org_code=decoded_token.org_code))
        return Response(org_code=decoded_token.org_code)
