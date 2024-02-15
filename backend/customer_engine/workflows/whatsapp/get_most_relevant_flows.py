"""Get most relevant flows workflow."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import UUID

from lego_workflows.components import Command, DomainError, DomainEvent, Response
from sqlalchemy import bindparam, text

from customer_engine.core import global_config
from customer_engine.core.whatsapp_flows import (
    WhatsAppFlow,
    embed_description_and_prompt,
)

if TYPE_CHECKING:
    from sqlalchemy import Connection


class NoRelevantWhatsappWorkflowError(DomainError):  # noqa: D101
    def __init__(self) -> None:  # noqa: D107
        super().__init__("No relevant whatsapp workflow found.")


@dataclass(frozen=True)
class GetMostRelevantFlowResponse(Response):
    """Response data for most relevant flows workflow."""

    most_revelant: WhatsAppFlow


@dataclass(frozen=True)
class GetMostRelevantFlowCommand(Command[GetMostRelevantFlowResponse, None]):
    """Input data for most revelant flow workflow."""

    org_code: str
    prompt: str
    conn: Connection

    async def run(  # noqa: D102
        self,
        state_changes: list[None],  # noqa: ARG002
        events: list[DomainEvent],  # noqa: ARG002
    ) -> GetMostRelevantFlowResponse:
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

        relevant_flow = self.conn.execute(
            text(
                """
            SELECT
                org_code,
                flow_id,
                name,
                description,
                embedding_model
            FROM whatsapp_flows
            WHERE
                org_code = :org_code AND
                flow_id = :relevant_flows
        """
            ).bindparams(
                bindparam(
                    key="relevant_flows",
                    value=UUID(most_relevant.id),
                ),
                bindparam(key="org_code", value=self.org_code),
            )
        ).one()

        return GetMostRelevantFlowResponse(
            most_revelant=WhatsAppFlow.from_dict(relevant_flow._asdict())
        )
