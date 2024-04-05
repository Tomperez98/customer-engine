"""Get similar example by prompt."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import UUID

import lego_workflows
from lego_workflows.components import (
    CommandComponent,
    DomainError,
    DomainEvent,
    ResponseComponent,
)
from qdrant_client.models import PointIdsList

from customer_engine_api.core import automatic_responses
from customer_engine_api.handlers.automatic_responses import get_example
from customer_engine_api.handlers.org_settings import get_or_default

if TYPE_CHECKING:
    import cohere
    from qdrant_client import AsyncQdrantClient
    from sqlalchemy import Connection

    from customer_engine_api.core.automatic_responses import Example


class NoSimilarExampleFoundError(DomainError):
    """Raised when no similar example is found."""

    def __init__(self, org_code: str) -> None:  # noqa: D107
        super().__init__(f"No similar example found in org {org_code}")


@dataclass(frozen=True)
class Response(ResponseComponent):  # noqa: D101
    example: Example


@dataclass(frozen=True)
class Command(CommandComponent[Response]):  # noqa: D101
    org_code: str
    prompt: str
    qdrant_client: AsyncQdrantClient
    cohere_client: cohere.AsyncClient
    sql_conn: Connection

    async def run(self, events: list[DomainEvent]) -> Response:  # noqa: ARG002, D102
        embedding_model_to_use = (
            await lego_workflows.run_and_collect_events(
                cmd=get_or_default.Command(
                    org_code=self.org_code, sql_conn=self.sql_conn
                )
            )
        )[0].settings.embeddings_model

        prompt_embeddings: list[
            list[float]
        ] = await automatic_responses.embeddings.embed_prompt_or_examples(
            client=self.cohere_client,
            model=embedding_model_to_use,
            prompt_or_examples=self.prompt,
        )

        while True:
            similar_points = await self.qdrant_client.search(
                collection_name=self.org_code,
                query_vector=prompt_embeddings[0],
                limit=5,
                score_threshold=0.80,
            )
            if len(similar_points) == 0:
                raise NoSimilarExampleFoundError(org_code=self.org_code)

            example: Example | None = None
            for similar_point in similar_points:
                if isinstance(similar_point.id, int):
                    msg = "Point ID type mismatch"
                    raise TypeError(msg)
                try:
                    example = (
                        await lego_workflows.run_and_collect_events(
                            get_example.Command(
                                org_code=self.org_code,
                                example_id=UUID(similar_point.id),
                                sql_conn=self.sql_conn,
                                automatic_response_id=None,
                            )
                        )
                    )[0].example

                except get_example.ExampleNotFoundError:
                    await self.qdrant_client.delete(
                        collection_name=self.org_code,
                        points_selector=PointIdsList(points=[similar_point.id]),
                    )

            if example is not None:
                break

        return Response(example=example)
