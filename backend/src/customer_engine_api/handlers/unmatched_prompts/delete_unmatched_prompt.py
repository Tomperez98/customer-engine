"""Delete unmatched prompt."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import sqlalchemy
from lego_workflows.components import CommandComponent, DomainEvent, ResponseComponent
from sqlalchemy import Connection, bindparam, text

from customer_engine_api.core.logging import logger

if TYPE_CHECKING:
    from uuid import UUID


@dataclass(frozen=True)
class UnmatchedPromptDeleted(DomainEvent):
    org_code: str
    prompt_id: UUID

    async def publish(self) -> None:
        logger.debug(
            "Unmatched prompt {promp_id} has been deleted from organization {org_code}",
            prompt_id=self.prompt_id,
            org_code=self.org_code,
        )


@dataclass(frozen=True)
class Response(ResponseComponent): ...


@dataclass(frozen=True)
class Command(CommandComponent[Response]):
    org_code: str
    prompt_id: UUID
    sql_conn: Connection

    async def run(self, events: list[DomainEvent]) -> Response:
        self.sql_conn.execute(
            text("""
            DELETE FROM unmatched_prompts
            WHERE org_code = :org_code
                AND prompt_id = :prompt_id""").bindparams(
                bindparam(
                    key="org_code", value=self.org_code, type_=sqlalchemy.String()
                ),
                bindparam(
                    key="prompt_id", value=self.prompt_id, type_=sqlalchemy.UUID()
                ),
            )
        )
        events.append(
            UnmatchedPromptDeleted(org_code=self.org_code, prompt_id=self.prompt_id)
        )
        return Response()
