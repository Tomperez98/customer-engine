"""List unmatched prompts."""
from __future__ import annotations

from dataclasses import dataclass

import sqlalchemy
from lego_workflows.components import CommandComponent, DomainEvent, ResponseComponent
from sqlalchemy import Connection, bindparam, text

from customer_engine.core.unmatched_prompts.shared import UnmatchedPrompt


@dataclass(frozen=True)
class Response(ResponseComponent):  # noqa: D101
    unmatched_prompts: list[UnmatchedPrompt]


@dataclass(frozen=True)
class Command(CommandComponent[Response]):  # noqa: D101
    org_code: str
    sql_conn: Connection

    async def run(self, events: list[DomainEvent]) -> Response:  # noqa: ARG002, D102
        stmt = text(
            """SELECT
                org_code,
                prompt_id,
                prompt
            FROM unmatched_prompts
            WHERE org_code = :org_code
            """
        ).bindparams(
            bindparam(key="org_code", value=self.org_code, type_=sqlalchemy.String())
        )

        return Response(
            unmatched_prompts=[
                UnmatchedPrompt.from_row(row=row)
                for row in self.sql_conn.execute(stmt).fetchall()
            ]
        )