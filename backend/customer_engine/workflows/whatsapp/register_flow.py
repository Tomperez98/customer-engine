"""Register flow workflow."""
from __future__ import annotations

import datetime
from dataclasses import dataclass

from lego_workflows.components import Command, DomainError, DomainEvent, Response
from sqlalchemy import Connection, TextClause, text

from customer_engine import logger
from customer_engine.core.whatsapp_flows import WhatsAppFlow
from customer_engine.workflows.whatsapp import get_flow


class WhatsAppFlowAlreadyExistsError(DomainError):
    """Raised when a whatsapp flow already exists."""

    def __init__(self, flow_id: str) -> None:  # noqa: D107
        super().__init__(f"WhatsApp flow with id {flow_id} already exists.")


@dataclass(frozen=True)
class NewWhatsAppFlowRegistered(DomainEvent):
    """Raised when a Whatsapp Flow has been registered."""

    flow_id: str
    registered_at: datetime.datetime

    async def publish(self) -> None:
        """Publish event."""
        logger.info(
            "New flow ID {flow_id} has been registered at {registered_at}",
            flow_id=self.flow_id,
            registered_at=self.registered_at,
        )


@dataclass(frozen=True)
class RegisterFlowResponse(Response):
    """Response data to register flow workflow."""

    register_at: datetime.datetime


@dataclass(frozen=True)
class RegisterFlowCommand(Command[RegisterFlowResponse, TextClause]):
    """Input data for register flow workflow."""

    flow_id: str
    name: str
    description: str
    conn: Connection

    async def run(
        self, state_changes: list[TextClause], events: list[DomainEvent]
    ) -> RegisterFlowResponse:
        """Execuet register flow command."""
        flow_exists: bool = False
        try:
            get_flow.GetFlowCommand(flow_id=self.flow_id, conn=self.conn)
        except get_flow.WhatsAppFlowNotFoundError:
            flow_exists = True

        if flow_exists:
            raise WhatsAppFlowAlreadyExistsError(flow_id=self.flow_id)

        WhatsAppFlow(
            flow_id=self.flow_id,
            name=self.name,
            description=self.description,
        ).to_dict()
        state_changes.append(
            text(
                """
                INSERT INTO whatsapp_flows (
                flow_id,
                name,
                description
                )
                VALUES (
                :flow_id,
                :name,
                :description
                )
                """
            ).bindparams(
                flow_id=self.flow_id, name=self.name, description=self.description
            )
        )
        now = datetime.datetime.now(tz=datetime.UTC)
        events.append(
            NewWhatsAppFlowRegistered(flow_id=self.flow_id, registered_at=now)
        )
        return RegisterFlowResponse(register_at=now)
