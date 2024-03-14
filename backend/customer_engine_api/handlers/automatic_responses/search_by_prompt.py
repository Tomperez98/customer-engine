"""Search automatic response by prompt."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import UUID

import lego_workflows
from lego_workflows.components import CommandComponent, DomainEvent, ResponseComponent
from qdrant_client.models import PointIdsList, ScoredPoint

from customer_engine_api.core import automatic_responses
from customer_engine_api.handlers.automatic_responses import get
from customer_engine_api.handlers.unmatched_prompts import register

if TYPE_CHECKING:
    import cohere
    from qdrant_client import AsyncQdrantClient
    from sqlalchemy import Connection


@dataclass(frozen=True)
class Response(ResponseComponent):  # noqa: D101
    response_or_unmatched_prompt_id: automatic_responses.AutomaticResponse | UUID


@dataclass(frozen=True)
class Command(CommandComponent[Response]):  # noqa: D101
    org_code: str
    prompt: str
    sql_conn: Connection
    cohere_client: cohere.AsyncClient
    qdrant_client: AsyncQdrantClient

    async def _register_unmatched_prompt(self, events: list[DomainEvent]) -> Response:
        (
            unmatched_prompt,
            register_prompt_events,
        ) = await lego_workflows.run_and_collect_events(
            register.Command(
                org_code=self.org_code,
                prompt=self.prompt,
                sql_conn=self.sql_conn,
            )
        )
        events.extend(register_prompt_events)
        return Response(
            response_or_unmatched_prompt_id=unmatched_prompt.prompt_id,
        )

    async def _get_automatic_response(
        self, most_relevant: ScoredPoint
    ) -> automatic_responses.AutomaticResponse:
        if isinstance(most_relevant.id, int):
            msg = "Most relevant id type not expected."
            raise TypeError(msg)

        return (
            await lego_workflows.run_and_collect_events(
                get.Command(
                    org_code=self.org_code,
                    automatic_response_id=UUID(most_relevant.id),
                    sql_conn=self.sql_conn,
                )
            )
        )[0].automatic_response

    async def run(self, events: list[DomainEvent]) -> Response:  # noqa: D102
        embedding_model_to_use = automatic_responses.embeddings.DEFAULT_EMBEDDING_MODEL
        prompt_embeddings = (
            await automatic_responses.embeddings.embed_examples_and_prompt(
                client=self.cohere_client,
                model=embedding_model_to_use,
                examples_or_prompt=self.prompt,
            )
        )
        while True:
            relevant_points = await self.qdrant_client.search(
                collection_name=self.org_code,
                query_vector=prompt_embeddings[0],
                limit=5,
                score_threshold=0.65,
            )

            if len(relevant_points) == 0:
                return await self._register_unmatched_prompt(events=events)

            automatic_response: automatic_responses.AutomaticResponse | None = None
            for relevant_point in relevant_points:
                try:
                    automatic_response = await self._get_automatic_response(
                        most_relevant=relevant_point
                    )
                except get.AutomaticResponseNotFoundError:
                    await self.qdrant_client.delete(
                        collection_name=self.org_code,
                        points_selector=PointIdsList(points=[relevant_point.id]),
                    )

            if automatic_response is not None:
                break

        return Response(
            response_or_unmatched_prompt_id=automatic_response,
        )
