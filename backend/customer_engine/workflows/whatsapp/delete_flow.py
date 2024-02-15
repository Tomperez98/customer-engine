"""Delete flow workflow."""
from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import TYPE_CHECKING

from lego_workflows.components import Command, DomainEvent, Response
from qdrant_client.http.models import PointIdsList
from sqlalchemy import Connection, TextClause, text

from customer_engine import logger
from customer_engine.core import global_config
from customer_engine.workflows.whatsapp import get_flow

if TYPE_CHECKING:
    from uuid import UUID


@dataclass(frozen=True)
class DeleteFlowResponse(Response):
    """Response data to delete flow workflow."""

    deleted_at: datetime.datetime


@dataclass(frozen=True)
class WhatsAppFlowHasBeenDeleted(DomainEvent):  # noqa: D101
    org_code: str
    flow_id: UUID

    async def publish(self) -> None:  # noqa: D102
        logger.info(
            "Flow {flow_id} from organization {org_code} has been deleted.",
            flow_id=self.flow_id,
            org_code=self.org_code,
        )


@dataclass(frozen=True)
class DeleteFlow(Command[DeleteFlowResponse, TextClause]):
    """Input data for delete flow workflow."""

    flow_id: UUID
    org_code: str
    conn: Connection

    async def run(
        self, state_changes: list[TextClause], events: list[DomainEvent]
    ) -> DeleteFlowResponse:
        """Execute delete flow workflow."""
        now = datetime.datetime.now(tz=datetime.UTC)

        await get_flow.GetFlowCommand(
            flow_id=self.flow_id, org_code=self.org_code, conn=self.conn
        ).run(state_changes=state_changes, events=events)

        await global_config.clients.qdrant.delete(
            collection_name=self.org_code,
            points_selector=PointIdsList(points=[self.flow_id.hex]),
        )
        state_changes.append(
            text(
                """
            DELETE FROM whatsapp_flows
            WHERE org_code = :org_code AND flow_id = :flow_id
        """
            ).bindparams(flow_id=self.flow_id, org_code=self.org_code)
        )
        events.append(
            WhatsAppFlowHasBeenDeleted(flow_id=self.flow_id, org_code=self.org_code)
        )
        return DeleteFlowResponse(deleted_at=now)
