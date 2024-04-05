from __future__ import annotations  # noqa: D100

from collections import Counter
from dataclasses import dataclass
from typing import TYPE_CHECKING, assert_never
from uuid import UUID

import lego_workflows
from lego_workflows.components import CommandComponent, DomainEvent, ResponseComponent

from customer_engine_api.handlers.automatic_responses import (
    get_auto_res,
    get_example,
    similar_examples_by_prompt,
)

if TYPE_CHECKING:
    import cohere
    from qdrant_client import AsyncQdrantClient
    from sqlalchemy import Connection

    from customer_engine_api.core.automatic_responses import AutomaticResponse


@dataclass(frozen=True)
class Response(ResponseComponent):  # noqa: D101
    automatic_response: AutomaticResponse


@dataclass(frozen=True)
class Command(CommandComponent[Response]):  # noqa: D101
    org_code: str
    example_id_or_prompt: UUID | str
    qdrant_client: AsyncQdrantClient
    cohere_client: cohere.AsyncClient
    sql_conn: Connection

    async def run(self, events: list[DomainEvent]) -> Response:  # noqa: ARG002, D102
        automatic_response_id: UUID
        match self.example_id_or_prompt:
            case UUID():
                example = (
                    await lego_workflows.run_and_collect_events(
                        get_example.Command(
                            org_code=self.org_code,
                            example_id=self.example_id_or_prompt,
                            sql_conn=self.sql_conn,
                            automatic_response_id=None,
                        )
                    )
                )[0].example
                automatic_response_id = example.automatic_response_id

            case str():
                examples = (
                    await lego_workflows.run_and_collect_events(
                        similar_examples_by_prompt.Command(
                            org_code=self.org_code,
                            prompt=self.example_id_or_prompt,
                            sql_conn=self.sql_conn,
                            qdrant_client=self.qdrant_client,
                            cohere_client=self.cohere_client,
                        )
                    )
                )[0].examples

                automatic_response_id = Counter(
                    example.automatic_response_id for example in examples
                ).most_common()[0][0]

            case _:
                assert_never(self.example_id_or_prompt)

        automatic_response = (
            await lego_workflows.run_and_collect_events(
                cmd=get_auto_res.Command(
                    org_code=self.org_code,
                    automatic_response_id=automatic_response_id,
                    sql_conn=self.sql_conn,
                )
            )
        )[0].automatic_response

        return Response(automatic_response=automatic_response)
