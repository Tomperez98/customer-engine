"""Update automatic response."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import lego_workflows
import sqlalchemy
from lego_workflows.components import CommandComponent, DomainEvent, ResponseComponent
from qdrant_client.http.models import Batch
from sqlalchemy import bindparam, text

from customer_engine.commands.automatic_responses import get
from customer_engine.commands.automatic_responses.core import (
    cohere_embed_examples_and_prompt,
)
from customer_engine.commands.automatic_responses.core.constants import (
    DEFAULT_EMBEDDING_MODEL,
)

if TYPE_CHECKING:
    from uuid import UUID

    import cohere
    from qdrant_client import AsyncQdrantClient
    from sqlalchemy import Connection

    from customer_engine.commands.automatic_responses.core import AutomaticResponse


@dataclass(frozen=True)
class Response(ResponseComponent):  # noqa: D101
    updated_automatic_response: AutomaticResponse
    new_embeddings_calculated: bool


@dataclass(frozen=True)
class Command(CommandComponent[Response]):  # noqa: D101
    org_code: str
    automatic_response_id: UUID
    new_name: str | None
    new_examples: list[str] | None
    new_response: str | None
    sql_conn: Connection
    cohere_client: cohere.AsyncClient
    qdrant_client: AsyncQdrantClient

    async def run(self, events: list[DomainEvent]) -> Response:  # noqa: ARG002, D102
        existing_automatic_response = (
            await lego_workflows.run_and_collect_events(
                cmd=get.Command(
                    org_code=self.org_code,
                    automatic_response_id=self.automatic_response_id,
                    sql_conn=self.sql_conn,
                )
            )
        )[0].automatic_response

        requires_new_embeddings: bool = False

        if self.new_name is not None:
            existing_automatic_response.name = self.new_name
        if self.new_examples is not None:
            existing_automatic_response.examples = self.new_examples
            requires_new_embeddings = True
        if self.new_response is not None:
            existing_automatic_response.response = self.new_response

        stmt = text(
            """
            UPDATE automatic_responses
            SET
                name = :name,
                examples = :examples,
                response = :response
            WHERE
                org_code = :org_code
                AND automatic_response_id = :automatic_response_id
            """
        ).bindparams(
            bindparam(
                key="org_code",
                value=existing_automatic_response.org_code,
                type_=sqlalchemy.String(),
            ),
            bindparam(
                key="automatic_response_id",
                value=existing_automatic_response.automatic_response_id,
                type_=sqlalchemy.UUID(),
            ),
            bindparam(
                key="name",
                value=existing_automatic_response.name,
                type_=sqlalchemy.String(),
            ),
            bindparam(
                key="examples",
                value=existing_automatic_response.examples,
                type_=sqlalchemy.JSON(),
            ),
            bindparam(
                key="response",
                value=existing_automatic_response.response,
                type_=sqlalchemy.String(),
            ),
        )
        self.sql_conn.execute(stmt)
        if not requires_new_embeddings:
            return Response(
                updated_automatic_response=existing_automatic_response,
                new_embeddings_calculated=requires_new_embeddings,
            )

        embedding_model_to_use = DEFAULT_EMBEDDING_MODEL

        new_examples_embeddings = await cohere_embed_examples_and_prompt(
            client=self.cohere_client,
            model=embedding_model_to_use,
            examples_or_prompt=existing_automatic_response.examples,
        )
        await self.qdrant_client.upsert(
            collection_name=self.org_code,
            points=Batch(
                ids=[existing_automatic_response.automatic_response_id.hex],
                vectors=new_examples_embeddings,
            ),
        )

        return Response(
            updated_automatic_response=existing_automatic_response,
            new_embeddings_calculated=requires_new_embeddings,
        )
