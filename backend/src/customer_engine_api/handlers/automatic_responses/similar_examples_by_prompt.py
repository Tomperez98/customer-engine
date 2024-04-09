"""Get similar example by prompt."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import UUID

import lego_workflows
from lego_workflows.components import (
    CommandComponent,
    DomainEvent,
    ResponseComponent,
)
from qdrant_client.models import PointIdsList

from customer_engine_api.core import automatic_responses
from customer_engine_api.handlers.automatic_responses import (
    get_bulk_examples,
)
from customer_engine_api.handlers.org_settings import get_or_default
from customer_engine_api.handlers.unmatched_prompts import register_unmatched_prompt

if TYPE_CHECKING:
    import datetime

    import cohere
    from qdrant_client import AsyncQdrantClient
    from sqlalchemy import Connection

    from customer_engine_api.core.automatic_responses import Example


@dataclass(frozen=True)
class Response(ResponseComponent):
    examples: list[Example]


@dataclass(frozen=True)
class Command(CommandComponent[Response]):
    org_code: str
    prompt: str
    current_time: datetime.datetime
    qdrant_client: AsyncQdrantClient
    cohere_client: cohere.AsyncClient
    sql_conn: Connection

    async def _get_similar_points_from_qdrant(
        self, promp_embeddings: list[float], up_to_n_points: int, score_threshold: float
    ) -> list[UUID]:
        similar_points: list[UUID] = []
        offset = 0
        points_per_query = up_to_n_points
        while True:
            if len(similar_points) >= up_to_n_points:
                break

            qdrant_similar_points = await self.qdrant_client.search(
                collection_name=self.org_code,
                query_vector=promp_embeddings,
                offset=offset,
                limit=points_per_query,
                score_threshold=score_threshold,
            )
            if len(qdrant_similar_points) == 0:
                break

            for qdrant_point in qdrant_similar_points:
                if isinstance(qdrant_point.id, int):
                    msg = "Point ID type mismatch"
                    raise TypeError(msg)

                similar_points.append(UUID(qdrant_point.id))

            offset += points_per_query

        return similar_points[:up_to_n_points]

    async def _register_unmatched_prompt(self, events: list[DomainEvent]) -> Response:
        (
            _,
            register_unmatched_prompt_events,
        ) = await lego_workflows.run_and_collect_events(
            register_unmatched_prompt.Command(
                org_code=self.org_code,
                prompt=self.prompt,
                current_time=self.current_time,
                sql_conn=self.sql_conn,
            )
        )
        events.extend(register_unmatched_prompt_events)
        return Response(examples=[])

    async def run(self, events: list[DomainEvent]) -> Response:
        if not (
            await self.qdrant_client.collection_exists(collection_name=self.org_code)
        ):
            return await self._register_unmatched_prompt(events=events)

        embedding_model_to_use = (
            await lego_workflows.run_and_collect_events(
                cmd=get_or_default.Command(
                    org_code=self.org_code, sql_conn=self.sql_conn
                )
            )
        )[0].settings.embeddings_model

        prompt_embeddings = (
            await automatic_responses.embeddings.embed_prompt_or_examples(
                client=self.cohere_client,
                model=embedding_model_to_use,
                prompt_or_examples=self.prompt,
            )
        )

        similar_points = await self._get_similar_points_from_qdrant(
            promp_embeddings=prompt_embeddings[0],
            up_to_n_points=10,
            score_threshold=0.80,
        )

        if len(similar_points) == 0:
            return await self._register_unmatched_prompt(events=events)

        examples = (
            await lego_workflows.run_and_collect_events(
                get_bulk_examples.Command(
                    org_code=self.org_code,
                    examples_ids=similar_points,
                    sql_conn=self.sql_conn,
                )
            )
        )[0].examples

        if len(examples) != len(similar_points):
            await self.qdrant_client.delete(
                collection_name=self.org_code,
                points_selector=PointIdsList(
                    points=[
                        point_id.hex
                        for point_id in set(similar_points).difference(
                            {example.example_id for example in examples}
                        )
                    ]
                ),
            )

        if len(examples) == 0:
            return await self._register_unmatched_prompt(events=events)

        return Response(examples=examples)
