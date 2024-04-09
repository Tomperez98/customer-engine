"""Bulk delete unmatched prompts."""

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
        logger.info(
            "Unmatched prompt {prompt_id} deleted from org {org_code}",
            prompt_id=self.prompt_id,
            org_code=self.org_code,
        )


@dataclass(frozen=True)
class Response(ResponseComponent): ...


@dataclass(frozen=True)
class Command(CommandComponent[Response]):
    org_code: str
    prompt_ids: list[UUID]
    sql_conn: Connection

    async def run(self, events: list[DomainEvent]) -> Response:
        stmt = text(
            """
            DELETE FROM unmatched_prompts
            WHERE org_code = :org_code
            AND prompt_id IN :prompt_ids
            """
        ).bindparams(
            bindparam(key="org_code", value=self.org_code, type_=sqlalchemy.String()),
            bindparam(
                key="prompt_ids",
                value=(prompt_id.hex for prompt_id in self.prompt_ids),
                type_=sqlalchemy.ARRAY(sqlalchemy.UUID()),
                expanding=True,
            ),
        )

        self.sql_conn.execute(stmt)

        events.extend(
            UnmatchedPromptDeleted(org_code=self.org_code, prompt_id=prompt_id)
            for prompt_id in self.prompt_ids
        )

        return Response()
