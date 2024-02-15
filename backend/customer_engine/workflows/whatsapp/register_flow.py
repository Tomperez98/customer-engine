"""Register flow workflow."""
from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import uuid4

from lego_workflows.components import Command, DomainError, DomainEvent, Response
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.http.models import Batch, VectorParams
from sqlalchemy import Connection, TextClause, text

from customer_engine import logger
from customer_engine.core import global_config
from customer_engine.core.whatsapp_flows import (
    embed_description_and_prompt,
    model_props,
)
from customer_engine.workflows.whatsapp import get_flow

if TYPE_CHECKING:
    from uuid import UUID


class WhatsAppFlowAlreadyExistsError(DomainError):
    """Raised when a whatsapp flow already exists."""

    def __init__(self, flow_id: UUID, org_code: str) -> None:  # noqa: D107
        super().__init__(
            f"WhatsApp flow with id {flow_id} already exists in org {org_code}."
        )


@dataclass(frozen=True)
class NewWhatsAppFlowRegistered(DomainEvent):
    """Raised when a Whatsapp Flow has been registered."""

    org_code: str
    flow_id: UUID
    registered_at: datetime.datetime

    async def publish(self) -> None:
        """Publish event."""
        logger.info(
            "New flow ID {flow_id} has been registered at {registered_at} for org {org_code}",
            flow_id=self.flow_id,
            registered_at=self.registered_at,
            org_code=self.org_code,
        )


@dataclass(frozen=True)
class RegisterFlowResponse(Response):
    """Response data to register flow workflow."""

    flow_id: UUID
    register_at: datetime.datetime


@dataclass(frozen=True)
class RegisterFlowCommand(Command[RegisterFlowResponse, TextClause]):
    """Input data for register flow workflow."""

    org_code: str
    name: str
    description: str
    conn: Connection

    async def run(
        self, state_changes: list[TextClause], events: list[DomainEvent]
    ) -> RegisterFlowResponse:
        """Execuet register flow command."""
        random_flow_id = uuid4()
        configured_model_props = model_props(model=global_config.default_model)
        while True:
            try:
                await get_flow.GetFlowCommand(
                    flow_id=random_flow_id, conn=self.conn, org_code=self.org_code
                ).run(state_changes=[], events=events)
            except get_flow.WhatsAppFlowNotFoundError:
                break
            continue

        try:
            await global_config.clients.qdrant.get_collection(
                collection_name=self.org_code,
            )
        except UnexpectedResponse:
            collection_created = await global_config.clients.qdrant.create_collection(
                collection_name=self.org_code,
                vectors_config=VectorParams(
                    size=configured_model_props.size,
                    distance=configured_model_props.distance,
                ),
            )
            if not collection_created:
                msg = "Unable to create collection"
                raise RuntimeError(msg) from None

        description_embeddings = await embed_description_and_prompt(
            cohere=global_config.clients.cohere,
            model=global_config.default_model,
            description=self.description,
        )

        await global_config.clients.qdrant.upsert(
            collection_name=self.org_code,
            points=Batch(
                ids=[random_flow_id.hex],
                vectors=description_embeddings,
            ),
        )

        state_changes.append(
            text(
                """
                INSERT INTO whatsapp_flows (
                org_code,
                flow_id,
                name,
                description,
                embedding_model
                )
                VALUES (
                :org_code,
                :flow_id,
                :name,
                :description,
                :embedding_model
                )
                """
            ).bindparams(
                org_code=self.org_code,
                flow_id=random_flow_id,
                name=self.name,
                description=self.description,
                embedding_model=global_config.default_model,
            )
        )
        now = datetime.datetime.now(tz=datetime.UTC)
        events.append(
            NewWhatsAppFlowRegistered(
                flow_id=random_flow_id, registered_at=now, org_code=self.org_code
            )
        )
        return RegisterFlowResponse(register_at=now, flow_id=random_flow_id)
