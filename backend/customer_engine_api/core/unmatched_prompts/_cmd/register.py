"""Register an unmatched prompt."""
from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import uuid4

import lego_workflows
import sqlalchemy
from lego_workflows.components import CommandComponent, DomainEvent, ResponseComponent
from sqlalchemy import Connection, bindparam, text

from customer_engine_api.core.unmatched_prompts._cmd import get
from customer_engine_api.logging import logger

if TYPE_CHECKING:
    from uuid import UUID


@dataclass(frozen=True)
class UnmatchedPromptRegistered(DomainEvent):
    """Indicated that an unmatched prompt has been registered."""

    org_code: str
    prompt_id: UUID
    registered_at: datetime.datetime

    async def publish(self) -> None:
        logger.debug(
            "Unmatched prompt {prompt_id} has been registered at {registered_at}",
            registered_at=self.registered_at,
            prompt_id=self.prompt_id,
        )


@dataclass(frozen=True)
class Response(ResponseComponent):
    prompt_id: UUID


@dataclass(frozen=True)
class Command(CommandComponent[Response]):
    org_code: str
    prompt: str
    sql_conn: Connection

    async def run(self, events: list[DomainEvent]) -> Response:
        while True:
            random_id = uuid4()
            try:
                await lego_workflows.run_and_collect_events(
                    cmd=get.Command(
                        org_code=self.org_code,
                        prompt_id=random_id,
                        sql_conn=self.sql_conn,
                    )
                )
            except get.UnmatchedResponseNotFoundError:
                break

        stmt = text(
            """
            INSERT INTO unmatched_prompts (
            org_code,
            prompt_id,
            prompt
            ) VALUES (
            :org_code,
            :prompt_id,
            :prompt
            )
            """
        ).bindparams(
            bindparam(key="org_code", value=self.org_code, type_=sqlalchemy.String()),
            bindparam(key="prompt_id", value=random_id, type_=sqlalchemy.UUID()),
            bindparam(key="prompt", value=self.prompt, type_=sqlalchemy.String()),
        )
        self.sql_conn.execute(stmt)

        events.append(
            UnmatchedPromptRegistered(
                prompt_id=random_id,
                org_code=self.org_code,
                registered_at=datetime.datetime.now(tz=datetime.UTC),
            )
        )
        return Response(prompt_id=random_id)
