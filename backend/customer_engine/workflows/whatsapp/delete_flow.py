"""Delete flow workflow."""
from __future__ import annotations

import datetime
from dataclasses import dataclass

from lego_workflows.components import Command, DomainEvent, Response
from sqlalchemy import Connection, TextClause, text

from customer_engine import logger
from customer_engine.workflows.whatsapp import get_flow


@dataclass(frozen=True)
class DeleteFlowResponse(Response):
    """Response data to delete flow workflow."""

    deleted_at: datetime.datetime
    flow_id: str


@dataclass(frozen=True)
class WhatsAppFlowHasBeenDeleted(DomainEvent):  # noqa: D101
    flow_id: str

    async def publish(self) -> None:  # noqa: D102
        logger.info(
            "Flow {flow_id} has been deleted.",
            flow_id=self.flow_id,
        )


@dataclass(frozen=True)
class DeleteFlow(Command[DeleteFlowResponse, TextClause]):
    """Input data for delete flow workflow."""

    flow_id: str
    conn: Connection

    async def run(
        self, state_changes: list[TextClause], events: list[DomainEvent]
    ) -> DeleteFlowResponse:
        """Execute delete flow workflow."""
        now = datetime.datetime.now(tz=datetime.UTC)

        await get_flow.GetFlowCommand(flow_id=self.flow_id, conn=self.conn).run(
            state_changes=state_changes, events=events
        )

        state_changes.append(
            text(
                """
            DELETE FROM whatsapp_flows
            WHERE flow_id = :flow_id
        """
            ).bindparams(flow_id=self.flow_id)
        )
        events.append(WhatsAppFlowHasBeenDeleted(flow_id=self.flow_id))
        return DeleteFlowResponse(deleted_at=now, flow_id=self.flow_id)
