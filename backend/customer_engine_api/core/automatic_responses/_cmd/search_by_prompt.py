"""Search automatic response by prompt."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import UUID

import lego_workflows
from lego_workflows.components import CommandComponent, DomainEvent, ResponseComponent

from customer_engine_api.core import unmatched_prompts
from customer_engine_api.core.automatic_responses._cmd import get
from customer_engine_api.core.automatic_responses.core import (
    DEFAULT_EMBEDDING_MODEL,
    AutomaticResponse,
    cohere_embed_examples_and_prompt,
)

if TYPE_CHECKING:
    import cohere
    from qdrant_client import AsyncQdrantClient
    from sqlalchemy import Connection


@dataclass(frozen=True)
class Response(ResponseComponent):
    automatic_response: AutomaticResponse | None
    unmatched_prompt_id: UUID | None


@dataclass(frozen=True)
class Command(CommandComponent[Response]):
    org_code: str
    prompt: str
    sql_conn: Connection
    cohere_client: cohere.AsyncClient
    qdrant_client: AsyncQdrantClient

    async def run(self, events: list[DomainEvent]) -> Response:
        embedding_model_to_use = DEFAULT_EMBEDDING_MODEL
        prompt_embeddings = await cohere_embed_examples_and_prompt(
            client=self.cohere_client,
            model=embedding_model_to_use,
            examples_or_prompt=self.prompt,
        )
        relevant_points = await self.qdrant_client.search(
            collection_name=self.org_code,
            query_vector=prompt_embeddings[0],
            limit=1,
            score_threshold=0.65,
        )

        if len(relevant_points) == 0:
            (
                unmatched_prompt,
                register_prompt_events,
            ) = await lego_workflows.run_and_collect_events(
                unmatched_prompts.cmd.register.Command(
                    org_code=self.org_code,
                    prompt=self.prompt,
                    sql_conn=self.sql_conn,
                )
            )
            events.extend(register_prompt_events)
            return Response(
                automatic_response=None,
                unmatched_prompt_id=unmatched_prompt.prompt_id,
            )

        most_relevant = relevant_points[0]
        if isinstance(most_relevant.id, int):
            msg = "Most relevant id type not expected."
            raise TypeError(msg)

        relevant_automatic_response = (
            await lego_workflows.run_and_collect_events(
                get.Command(
                    org_code=self.org_code,
                    automatic_response_id=UUID(most_relevant.id),
                    sql_conn=self.sql_conn,
                )
            )
        )[0].automatic_response

        return Response(
            automatic_response=relevant_automatic_response,
            unmatched_prompt_id=None,
        )
