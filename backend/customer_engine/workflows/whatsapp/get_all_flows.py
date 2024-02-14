"""Get all flows workflow."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import orjson
from lego_workflows.components import Command, DomainEvent, Response
from sqlalchemy import Connection, Row, TextClause, text

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
                description,
                metadata
            FROM whatsapp_flows"""
            )
        ).fetchall()

        existing_workflows: list[WhatsAppFlow] = [
            _parse_row(workflow) for workflow in all_workflows
        ]

        return GetAllWhatsAppFlowsResponse(flows=existing_workflows)


def _parse_row(row: Row[Any]) -> WhatsAppFlow:
    row_data = row._asdict()
    row_data["metadata"] = orjson.loads(row_data["metadata"])
    return WhatsAppFlow.from_dict(row_data)
