"""Get flow workflow."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from lego_workflows.components import Command, DomainError, DomainEvent, Response
from sqlalchemy import Connection, text

from customer_engine.core.whatsapp_flows import WhatsAppFlow

if TYPE_CHECKING:
    from uuid import UUID


class WhatsAppFlowNotFoundError(DomainError):
    """Raised when whatsapp flow does not exists."""

    def __init__(self, flow_id: UUID, org_code: str) -> None:  # noqa: D107
        super().__init__(f"Whatsapp flow {flow_id} from org {org_code} not found.")


@dataclass(frozen=True)
class GetFlowResponse(Response):
    """Response data for get flow workflow."""

    flow: WhatsAppFlow


@dataclass(frozen=True)
class GetFlowCommand(Command[GetFlowResponse, None]):
    """Input data for get flow workflow."""

    org_code: str
    flow_id: UUID
    conn: Connection

    async def run(
        self,
        state_changes: list[None],  # noqa: ARG002
        events: list[DomainEvent],  # noqa: ARG002
    ) -> GetFlowResponse:
        """Execute get flow workflow."""
        whatsapp_flow = self.conn.execute(
            text(
                """
            SELECT
                org_code,
                flow_id,
                name,
                description,
                embedding_model
            FROM whatsapp_flows
            WHERE org_code = :org_code AND flow_id = :flow_id
"""
            ).bindparams(flow_id=self.flow_id, org_code=self.org_code)
        ).fetchone()
        if whatsapp_flow is None:
            raise WhatsAppFlowNotFoundError(
                flow_id=self.flow_id, org_code=self.org_code
            )

        return GetFlowResponse(flow=WhatsAppFlow.from_dict(whatsapp_flow._asdict()))
