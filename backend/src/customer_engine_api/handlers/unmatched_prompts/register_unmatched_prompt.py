"""Register unmatched prompt."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import uuid4

import lego_workflows
import sqlalchemy
from lego_workflows.components import CommandComponent, DomainEvent, ResponseComponent
from sqlalchemy import Connection, bindparam, text

from customer_engine_api.core.logging import logger
from customer_engine_api.handlers.unmatched_prompts import get_unmatched_prompt

if TYPE_CHECKING:
    import datetime
    from uuid import UUID


@dataclass(frozen=True)
class UnmatchedPromptRegistered(DomainEvent):
    org_code: str
    unmatched_prompt_id: UUID

    async def publish(self) -> None:
        logger.info(
            "Unmatched prompt with ID {unmatched_prompt_id} registered for organization {org_code}",
            unmatched_prompt_id=self.unmatched_prompt_id,
            org_code=self.org_code,
        )


@dataclass(frozen=True)
class Response(ResponseComponent):
    umatched_prompt_id: UUID


@dataclass(frozen=True)
class Command(CommandComponent[Response]):
    org_code: str
    prompt: str
    current_time: datetime.datetime
    sql_conn: Connection

    async def run(self, events: list[DomainEvent]) -> Response:
        while True:
            random_id = uuid4()
            try:
                await lego_workflows.run_and_collect_events(
                    cmd=get_unmatched_prompt.Command(
                        org_code=self.org_code,
                        prompt_id=random_id,
                        sql_conn=self.sql_conn,
                    )
                )
            except get_unmatched_prompt.UnmatchedPromptNotFoundError:
                break

        self.sql_conn.execute(
            text(
                """
            INSERT INTO unmatched_prompts (
                org_code,
                prompt_id,
                prompt,
                created_at
            ) VALUES (
                :org_code,
                :prompt_id,
                :prompt,
                :created_at
            )
                """
            ).bindparams(
                bindparam(
                    key="org_code", value=self.org_code, type_=sqlalchemy.String()
                ),
                bindparam(key="prompt_id", value=random_id, type_=sqlalchemy.UUID()),
                bindparam(key="prompt", value=self.prompt, type_=sqlalchemy.String()),
                bindparam(
                    key="created_at",
                    value=self.current_time,
                    type_=sqlalchemy.DateTime(timezone=True),
                ),
            )
        )

        events.append(
            UnmatchedPromptRegistered(self.org_code, unmatched_prompt_id=random_id)
        )

        return Response(umatched_prompt_id=random_id)
