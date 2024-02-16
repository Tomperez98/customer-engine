"""Update form workflow."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from lego_workflows.components import CommandComponent, DomainEvent, ResponseComponent
from qdrant_client.http.models import Batch
from sqlalchemy import Connection, TextClause, text

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
        self, state_changes: list[TextClause], events: list[DomainEvent]
    ) -> Response:
        response = await get_form.Command(
            form_id=self.form_id, conn=self.conn, org_code=self.org_code
        ).run(state_changes=[], events=events)

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
        state_changes.append(
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
                name=existing_flow.name,
                description=existing_flow.description,
                form_id=existing_flow.form_id,
                embedding_model=existing_flow.embedding_model,
            )
        )

        events.append(FormsHasBeenUpdated(form_id=self.form_id, org_code="test"))
        return Response(flow=existing_flow)
