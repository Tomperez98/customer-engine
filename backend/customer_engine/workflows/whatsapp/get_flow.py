"""Get flow workflow."""
from __future__ import annotations

from dataclasses import dataclass

from lego_workflows.components import Command, DomainError, DomainEvent, Response
from sqlalchemy import Connection, TextClause, text

from customer_engine.core.whatsapp_flows import WhatsAppFlow


class WhatsAppFlowNotFoundError(DomainError):
    """Raised when whatsapp flow does not exists."""

    def __init__(self, flow_id: str) -> None:  # noqa: D107
        super().__init__(f"Whatsapp flow {flow_id} not found.")


@dataclass(frozen=True)
class GetFlowResponse(Response):
    """Response data for get flow workflow."""

    flow: WhatsAppFlow


@dataclass(frozen=True)
class GetFlowCommand(Command[GetFlowResponse, TextClause]):
    """Input data for get flow workflow."""

    flow_id: str
    conn: Connection

    async def run(
        self,
        state_changes: list[TextClause],  # noqa: ARG002
        events: list[DomainEvent],  # noqa: ARG002
    ) -> GetFlowResponse:
        """Execute get flow workflow."""
        whatsapp_flow = self.conn.execute(
            text(
                """
            SELECT
                flow_id,
                name,
                description
            FROM whatsapp_flows
            WHERE flow_id = :flow_id
"""
            ).bindparams(flow_id=self.flow_id)
        ).fetchone()
        if whatsapp_flow is None:
            raise WhatsAppFlowNotFoundError(flow_id=self.flow_id)

        return GetFlowResponse(flow=WhatsAppFlow.from_dict(whatsapp_flow._asdict()))
