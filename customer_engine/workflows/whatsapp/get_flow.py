"""Get flow workflow."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import orjson
from lego_workflows.components import Command, DomainError, DomainEvent, Response
from sqlalchemy import Connection, Row, TextClause, text

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
                description,
                metadata
            FROM whatsapp_flows
            WHERE flow_id = :flow_id
"""
            ).bindparams(flow_id=self.flow_id)
        ).fetchone()
        if whatsapp_flow is None:
            raise WhatsAppFlowNotFoundError(flow_id=self.flow_id)

        return GetFlowResponse(flow=_parse_row(row=whatsapp_flow))


def _parse_row(row: Row[Any]) -> WhatsAppFlow:
    row_data = row._asdict()
    row_data["metadata"] = orjson.loads(row_data["metadata"])
    return WhatsAppFlow.from_dict(row_data)
