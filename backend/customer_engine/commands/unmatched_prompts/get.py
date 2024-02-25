"""Get unmatch prompt."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import sqlalchemy
from lego_workflows.components import (
    CommandComponent,
    DomainError,
    DomainEvent,
    ResponseComponent,
)
from sqlalchemy import Connection, bindparam, text

from customer_engine.commands.unmatched_prompts.core import UnmatchedPrompt

if TYPE_CHECKING:
    from uuid import UUID


class UnmatchedResponseNotFoundError(DomainError):
    """Raised when an unmatched response is not found."""

    def __init__(self, org_code: str, prompt_id: UUID) -> None:
        super().__init__(
            f"Unmatched prompt with ID {prompt_id} not found for org {org_code}"
        )


@dataclass(frozen=True)
class Response(ResponseComponent):
    unmatched_prompt: UnmatchedPrompt


@dataclass(frozen=True)
class Command(CommandComponent[Response]):
    org_code: str
    prompt_id: UUID
    sql_conn: Connection

    async def run(self, events: list[DomainEvent]) -> Response:
        stmt = text(
            """SELECT
                org_code,
                prompt_id,
                prompt
            FROM unmatched_prompts
            WHERE org_code = :org_code
                AND prompt_id = :prompt_id
            """
        ).bindparams(
            bindparam(key="org_code", value=self.org_code, type_=sqlalchemy.String()),
            bindparam(
                key="prompt_id",
                value=self.prompt_id,
                type_=sqlalchemy.UUID(),
            ),
        )

        unmatched_prompt_row = self.sql_conn.execute(stmt).fetchone()
        if unmatched_prompt_row is None:
            raise UnmatchedResponseNotFoundError(
                org_code=self.org_code, prompt_id=self.prompt_id
            )

        return Response(
            unmatched_prompt=UnmatchedPrompt.from_row(row=unmatched_prompt_row)
        )
