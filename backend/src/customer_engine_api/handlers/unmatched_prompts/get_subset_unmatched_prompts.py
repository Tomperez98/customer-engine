"""Get subset unmatched prompts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import sqlalchemy
from lego_workflows.components import CommandComponent, DomainEvent, ResponseComponent
from sqlalchemy import Connection, bindparam, text

from customer_engine_api.core.automatic_responses import UnmatchedPrompt

if TYPE_CHECKING:
    from uuid import UUID


@dataclass(frozen=True)
class Response(ResponseComponent):
    unmatched_prompts: list[UnmatchedPrompt]


@dataclass(frozen=True)
class Command(CommandComponent[Response]):
    org_code: str
    prompt_ids: list[UUID]
    sql_conn: Connection

    async def run(self, events: list[DomainEvent]) -> Response:  # noqa: ARG002
        stmt = text(
            """
            SELECT
                org_code,
                prompt_id,
                prompt,
                created_at
            FROM unmatched_prompts
            WHERE org_code = :org_code
                AND prompt_id in :prompt_ids
            """
        ).bindparams(
            bindparam(key="org_code", value=self.org_code, type_=sqlalchemy.String()),
            bindparam(
                key="prompt_ids",
                value=(prompt_id.hex for prompt_id in self.prompt_ids),
                type_=sqlalchemy.ARRAY(sqlalchemy.String()),
                expanding=True,
            ),
        )
        return Response(
            unmatched_prompts=[
                UnmatchedPrompt.from_row(row=row)
                for row in self.sql_conn.execute(stmt).fetchall()
            ]
        )
