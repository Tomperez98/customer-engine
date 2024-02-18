"""Update form workflow."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import sqlalchemy
from lego_workflows.components import CommandComponent, DomainEvent, ResponseComponent
from qdrant_client.http.models import Batch
from sqlalchemy import Connection, TextClause, bindparam, text

from customer_engine import logger
from customer_engine.core import global_config
from customer_engine.core.forms import embed_description_and_prompt
from customer_engine.workflows.forms import get_form

if TYPE_CHECKING:
    from uuid import UUID

    from customer_engine.core.forms import Form


@dataclass(frozen=True)
class FormsHasBeenUpdated(DomainEvent):  # noqa: D101
    org_code: str
    form_id: UUID

    async def publish(self) -> None:  # noqa: D102
        logger.info(
            "Form {form_id} from org {org_code} has been updated.",
            form_id=self.form_id,
            org_code=self.org_code,
        )


@dataclass(frozen=True)
class Response(ResponseComponent):  # noqa: D101
    flow: Form


@dataclass(frozen=True)
class Command(CommandComponent[Response, TextClause]):  # noqa: D101
    org_code: str
    form_id: UUID
    name: str | None
    description: str | None
    conn: Connection

    async def run(  # noqa: D102
        self, events: list[DomainEvent]
    ) -> Response:
        response = await get_form.Command(
            form_id=self.form_id, conn=self.conn, org_code=self.org_code
        ).run(events=events)

        existing_flow = response.form

        if self.name is not None:
            existing_flow.name = self.name

        require_recalculate_embeddings: bool = False
        if self.description is not None:
            existing_flow.description = self.description
            require_recalculate_embeddings = True

        if existing_flow.embedding_model != global_config.default_model:
            existing_flow.embedding_model = global_config.default_model
            require_recalculate_embeddings = True

        self.conn.execute(
            text(
                """
                UPDATE forms
                SET
                    name = :name,
                    description = :description,
                    embedding_model = :embedding_model
                WHERE
                    form_id = :form_id
                """
            ).bindparams(
                bindparam(
                    key="name", value=existing_flow.name, type_=sqlalchemy.String()
                ),
                bindparam(
                    key="description",
                    value=existing_flow.description,
                    type_=sqlalchemy.String(),
                ),
                bindparam(
                    key="form_id", value=existing_flow.form_id, type_=sqlalchemy.UUID()
                ),
                bindparam(
                    key="embedding_model",
                    value=existing_flow.embedding_model,
                    type_=sqlalchemy.String(),
                ),
            )
        )

        if require_recalculate_embeddings:
            new_description_embeddings = await embed_description_and_prompt(
                cohere=global_config.clients.cohere,
                model=global_config.default_model,
                description=existing_flow.description,
            )
            await global_config.clients.qdrant.upsert(
                collection_name=self.org_code,
                points=Batch(
                    ids=[self.form_id.hex],
                    vectors=new_description_embeddings,
                ),
            )

        events.append(FormsHasBeenUpdated(form_id=self.form_id, org_code="test"))
        return Response(flow=existing_flow)
