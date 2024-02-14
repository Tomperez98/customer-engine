"""Update flow workflow."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from lego_workflows.components import Command, DomainEvent, Response
from sqlalchemy import Connection, TextClause, text

from customer_engine import logger
from customer_engine.workflows.whatsapp import get_flow

if TYPE_CHECKING:
    from customer_engine.core.whatsapp_flows import WhatsAppFlow


@dataclass(frozen=True)
class WhatsAppFlowHasBeenUpdated(DomainEvent):  # noqa: D101
    flow_id: str

    async def publish(self) -> None:  # noqa: D102
        logger.info("Flow {flow_id} has been updated.", flow_id=self.flow_id)


@dataclass(frozen=True)
class UpdateWhatsAppFlowResponse(Response):  # noqa: D101
    flow: WhatsAppFlow


@dataclass(frozen=True)
class UpdateWhatsAppFlowCommand(Command[UpdateWhatsAppFlowResponse, TextClause]):  # noqa: D101
    flow_id: str
    name: str | None
    description: str | None
    conn: Connection

    async def run(  # noqa: D102
        self, state_changes: list[TextClause], events: list[DomainEvent]
    ) -> UpdateWhatsAppFlowResponse:
        response = await get_flow.GetFlowCommand(
            flow_id=self.flow_id, conn=self.conn
        ).run(state_changes=state_changes, events=events)

        existing_flow = response.flow

        if self.name is not None:
            existing_flow.name = self.name

        if self.description is not None:
            existing_flow.description = self.description

        state_changes.append(
            text(
                """
                UPDATE whatsapp_flows
                SET
                    name = :name,
                    description = :description
                WHERE
                    flow_id = :flow_id
                """
            ).bindparams(
                name=existing_flow.name,
                description=existing_flow.description,
                flow_id=existing_flow.flow_id,
            )
        )

        events.append(WhatsAppFlowHasBeenUpdated(flow_id=self.flow_id))
        return UpdateWhatsAppFlowResponse(flow=existing_flow)
