"""Get all flows workflow."""
from __future__ import annotations

from dataclasses import dataclass

from lego_workflows.components import Command, DomainEvent, Response
from sqlalchemy import Connection, text

from customer_engine.core.whatsapp_flows import WhatsAppFlow


@dataclass(frozen=True)
class GetAllWhatsAppFlowsResponse(Response):
    """Get all whatsapp flows response data."""

    flows: list[WhatsAppFlow]


@dataclass(frozen=True)
class GetAllWhatsAppFlowsCommand(Command[GetAllWhatsAppFlowsResponse, None]):
    """Get all whatsapp flows input data."""

    org_code: str
    conn: Connection

    async def run(
        self,
        state_changes: list[None],  # noqa: ARG002
        events: list[DomainEvent],  # noqa: ARG002
    ) -> GetAllWhatsAppFlowsResponse:
        """Execute get all whatsapp flows."""
        all_workflows = self.conn.execute(
            text(
                """
            SELECT
                org_code,
                flow_id,
                name,
                description,
                embedding_model
            FROM whatsapp_flows
            WHERE org_code = :org_code"""
            ).bindparams(org_code=self.org_code)
        ).fetchall()

        return GetAllWhatsAppFlowsResponse(
            flows=[
                WhatsAppFlow.from_dict(workflow._asdict()) for workflow in all_workflows
            ]
        )
