"""Get most relevant flows workflow."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import UUID

from lego_workflows.components import (
    CommandComponent,
    DomainError,
    DomainEvent,
    ResponseComponent,
)

from customer_engine.core import global_config
from customer_engine.core.forms import (
    Form,
    FormConfig,
    embed_description_and_prompt,
)
from customer_engine.workflows.forms import get_form

if TYPE_CHECKING:
    from sqlalchemy import Connection


class NoRelevantWhatsappWorkflowError(DomainError):  # noqa: D101
    def __init__(self) -> None:  # noqa: D107
        super().__init__("No relevant whatsapp workflow found.")


@dataclass(frozen=True)
class Response(ResponseComponent):
    """Response data for most relevant flows workflow."""

    most_revelant: Form
    configuration: FormConfig


@dataclass(frozen=True)
class Command(CommandComponent[Response, None]):
    """Input data for most revelant flow workflow."""

    org_code: str
    prompt: str
    conn: Connection

    async def run(  # noqa: D102
        self,
        state_changes: list[None],
        events: list[DomainEvent],
    ) -> Response:
        prompt_embeddings = (
            await embed_description_and_prompt(
                cohere=global_config.clients.cohere,
                model=global_config.default_model,
                description=self.prompt,
            )
        )[0]

        relevant_points = await global_config.clients.qdrant.search(
            collection_name=self.org_code,
            query_vector=prompt_embeddings,
            limit=3,
            score_threshold=0.7,
        )
        if len(relevant_points) == 0:
            raise NoRelevantWhatsappWorkflowError
        most_relevant = relevant_points[0]
        if isinstance(most_relevant.id, int):
            msg = "Most relevant id type not expected."
            raise TypeError(msg)

        relevant_flow = await get_form.Command(
            org_code=self.org_code, form_id=UUID(most_relevant.id), conn=self.conn
        ).run(state_changes=state_changes, events=events)

        return Response(
            most_revelant=relevant_flow.form, configuration=relevant_flow.configuration
        )
