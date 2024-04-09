"""Get unmatched prompt."""

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

from customer_engine_api.core.automatic_responses import UnmatchedPrompt

if TYPE_CHECKING:
    from uuid import UUID


class UnmatchedPromptNotFoundError(DomainError):
    def __init__(self, org_code: str, prompt_id: UUID) -> None:
        super().__init__(f"Unmatched prompt {prompt_id} not found in org {org_code}")


@dataclass(frozen=True)
class Response(ResponseComponent):
    unmatched_prompt: UnmatchedPrompt


@dataclass(frozen=True)
class Command(CommandComponent[Response]):
    org_code: str
    prompt_id: UUID
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
                AND prompt_id = :prompt_id
            """
        ).bindparams(
            bindparam(
                key="org_code",
                value=self.org_code,
                type_=sqlalchemy.String(),
            ),
            bindparam(key="prompt_id", value=self.prompt_id, type_=sqlalchemy.UUID()),
        )

        row = self.sql_conn.execute(statement=stmt).one_or_none()
        if row is None:
            raise UnmatchedPromptNotFoundError(
                org_code=self.org_code,
                prompt_id=self.prompt_id,
            )

        return Response(unmatched_prompt=UnmatchedPrompt.from_row(row=row))
