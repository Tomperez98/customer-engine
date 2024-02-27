"""Add unmatched prompt as an example to automatic response."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import lego_workflows
from lego_workflows.components import CommandComponent, DomainEvent, ResponseComponent

from customer_engine.core import automatic_responses
from customer_engine.core.unmatched_prompts._cmd import delete, get
from customer_engine.logging import logger

if TYPE_CHECKING:
    from uuid import UUID

    import cohere
    from qdrant_client import AsyncQdrantClient
    from sqlalchemy import Connection


@dataclass(frozen=True)
class UnmatchedPromptHasBeenAddedAsExampleToAutomaticResponse(DomainEvent):
    """Indicated that an unmatched prompt has been added as example to automatic response."""

    org_code: str
    automatic_response_id: UUID
    prompt_id: UUID

    async def publish(self) -> None:
        logger.debug(
            "Prompt {prompt_id} has been added as an example to automatic response {automatic_response_id}",
            prompt_id=self.prompt_id,
            automatic_response_id=self.automatic_response_id,
        )


@dataclass(frozen=True)
class Response(ResponseComponent):
    prompt_id: UUID


@dataclass(frozen=True)
class Command(CommandComponent[Response]):
    org_code: str
    prompt_id: UUID
    autoamtic_response_id: UUID
    sql_conn: Connection
    cohere_client: cohere.AsyncClient
    qdrant_client: AsyncQdrantClient

    async def run(self, events: list[DomainEvent]) -> Response:
        automatic_response = (
            await lego_workflows.run_and_collect_events(
                cmd=automatic_responses.cmd.get.Command(
                    org_code=self.org_code,
                    automatic_response_id=self.autoamtic_response_id,
                    sql_conn=self.sql_conn,
                )
            )
        )[0].automatic_response
        unmatched_prompt = (
            await lego_workflows.run_and_collect_events(
                get.Command(
                    org_code=self.org_code,
                    prompt_id=self.prompt_id,
                    sql_conn=self.sql_conn,
                )
            )
        )[0].unmatched_prompt

        automatic_response.examples.append(unmatched_prompt.prompt)

        _, updated_events = await lego_workflows.run_and_collect_events(
            cmd=automatic_responses.cmd.update.Command(
                org_code=self.org_code,
                automatic_response_id=self.autoamtic_response_id,
                new_name=None,
                new_examples=automatic_response.examples,
                new_response=None,
                sql_conn=self.sql_conn,
                cohere_client=self.cohere_client,
                qdrant_client=self.qdrant_client,
            )
        )
        events.extend(updated_events)
        _, deleted_events = await lego_workflows.run_and_collect_events(
            delete.Command(
                org_code=self.org_code, prompt_id=self.prompt_id, sql_conn=self.sql_conn
            )
        )
        events.extend(deleted_events)
        events.append(
            UnmatchedPromptHasBeenAddedAsExampleToAutomaticResponse(
                self.org_code,
                automatic_response_id=self.autoamtic_response_id,
                prompt_id=self.prompt_id,
            )
        )
        return Response(prompt_id=self.prompt_id)
