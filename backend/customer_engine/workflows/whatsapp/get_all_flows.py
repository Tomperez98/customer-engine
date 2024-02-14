"""Get all flows workflow."""
from __future__ import annotations

from dataclasses import dataclass

from lego_workflows.components import Command, DomainEvent, Response
from sqlalchemy import Connection, TextClause, text

from customer_engine.core.whatsapp_flows import WhatsAppFlow


@dataclass(frozen=True)
class GetAllWhatsAppFlowsResponse(Response):
    """Get all whatsapp flows response data."""

    flows: list[WhatsAppFlow]


@dataclass(frozen=True)
class GetAllWhatsAppFlowsCommand(Command[GetAllWhatsAppFlowsResponse, TextClause]):
    """Get all whatsapp flows input data."""

    conn: Connection

    async def run(
        self,
        state_changes: list[TextClause],  # noqa: ARG002
        events: list[DomainEvent],  # noqa: ARG002
    ) -> GetAllWhatsAppFlowsResponse:
        """Execute get all whatsapp flows."""
        all_workflows = self.conn.execute(
            text(
                """
            SELECT
                flow_id,
                name,
                description
            FROM whatsapp_flows"""
            )
        ).fetchall()

        return GetAllWhatsAppFlowsResponse(
            flows=[
                WhatsAppFlow.from_dict(workflow._asdict()) for workflow in all_workflows
            ]
        )
