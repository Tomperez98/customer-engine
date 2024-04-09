"""Bulk add to automatic response as example."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import lego_workflows
from lego_workflows.components import CommandComponent, DomainEvent, ResponseComponent

from customer_engine_api.handlers import automatic_responses
from customer_engine_api.handlers.unmatched_prompts import (
    bulk_delete_unmatched_prompts,
    get_subset_unmatched_prompts,
)

if TYPE_CHECKING:
    from uuid import UUID

    import cohere
    from qdrant_client import AsyncQdrantClient
    from sqlalchemy import Connection


@dataclass(frozen=True)
class Response(ResponseComponent):
    example_ids: list[UUID]


@dataclass(frozen=True)
class Command(CommandComponent[Response]):
    org_code: str
    prompt_ids: list[UUID]
    automatic_response_id: UUID
    sql_conn: Connection
    qdrant_client: AsyncQdrantClient
    cohere_client: cohere.AsyncClient

    async def run(self, events: list[DomainEvent]) -> Response:
        (
            response_get_subset,
            get_subset_events,
        ) = await lego_workflows.run_and_collect_events(
            get_subset_unmatched_prompts.Command(
                org_code=self.org_code,
                prompt_ids=self.prompt_ids,
                sql_conn=self.sql_conn,
            )
        )
        events.extend(get_subset_events)

        _, delete_events = await lego_workflows.run_and_collect_events(
            bulk_delete_unmatched_prompts.Command(
                org_code=self.org_code,
                prompt_ids=self.prompt_ids,
                sql_conn=self.sql_conn,
            )
        )
        events.extend(delete_events)

        (
            create_example_response,
            create_example_events,
        ) = await lego_workflows.run_and_collect_events(
            automatic_responses.create_example.Command(
                org_code=self.org_code,
                examples=[
                    unmatched_prompt.prompt
                    for unmatched_prompt in response_get_subset.unmatched_prompts
                ],
                automatic_response_id=self.automatic_response_id,
                qdrant_client=self.qdrant_client,
                cohere_client=self.cohere_client,
                sql_conn=self.sql_conn,
            )
        )
        events.extend(create_example_events)

        return Response(example_ids=create_example_response.example_ids)
