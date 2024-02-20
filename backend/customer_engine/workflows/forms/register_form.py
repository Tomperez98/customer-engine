"""Register flow workflow."""
from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import uuid4

import sqlalchemy
from lego_workflows.components import (
    CommandComponent,
    DomainError,
    DomainEvent,
    ResponseComponent,
)
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.http.models import Batch, VectorParams
from sqlalchemy import Connection, TextClause, bindparam, text

from customer_engine import logger
from customer_engine.core import global_config
from customer_engine.core.forms import (
    FormConfig,
    embed_description_and_prompt,
    model_props,
)
from customer_engine.workflows.forms import get_form

if TYPE_CHECKING:
    from uuid import UUID


class FormsAlreadyExistsError(DomainError):
    """Raised when a whatsapp flow already exists."""

    def __init__(self, form_id: UUID, org_code: str) -> None:  # noqa: D107
        super().__init__(
            f"WhatsApp flow with id {form_id} already exists in org {org_code}."
        )


@dataclass(frozen=True)
class NewFormsRegistered(DomainEvent):
    """Raised when a Whatsapp Flow has been registered."""

    org_code: str
    form_id: UUID
    registered_at: datetime.datetime

    async def publish(self) -> None:
        """Publish event."""
        logger.info(
            "New flow ID {form_id} has been registered at {registered_at} for org {org_code}",
            form_id=self.form_id,
            registered_at=self.registered_at,
            org_code=self.org_code,
        )


@dataclass(frozen=True)
class Response(ResponseComponent):
    """Response data to register flow workflow."""

    form_id: UUID
    register_at: datetime.datetime


@dataclass(frozen=True)
class Command(CommandComponent[Response, TextClause]):
    """Input data for register flow workflow."""

    org_code: str
    name: str
    examples: list[str]
    configuration: FormConfig
    conn: Connection

    async def run(self, events: list[DomainEvent]) -> Response:
        """Execuet register flow command."""
        random_flow_id = uuid4()
        configured_model_props = model_props(model=global_config.default_model)
        while True:
            try:
                await get_form.Command(
                    form_id=random_flow_id, conn=self.conn, org_code=self.org_code
                ).run(events=events)
            except get_form.FormNotFoundError:
                break
            continue

        self.conn.execute(
            text(
                """INSERT INTO form_configs (
                org_code,
                form_id,
                configuration
                )
                VALUES (
                :org_code,
                :form_id,
                :configuration
                )"""
            ).bindparams(
                bindparam(
                    key="org_code", value=self.org_code, type_=sqlalchemy.String()
                ),
                bindparam(key="form_id", value=random_flow_id, type_=sqlalchemy.UUID()),
                bindparam(
                    key="configuration",
                    value=self.configuration.to_dict(),
                    type_=sqlalchemy.JSON(),
                ),
            )
        )

        self.conn.execute(
            text(
                """
                INSERT INTO forms (
                org_code,
                form_id,
                name,
                examples,
                embedding_model
                )
                VALUES (
                :org_code,
                :form_id,
                :name,
                :examples,
                :embedding_model
                )
                """
            ).bindparams(
                bindparam(
                    key="org_code", value=self.org_code, type_=sqlalchemy.String()
                ),
                bindparam(key="form_id", value=random_flow_id, type_=sqlalchemy.UUID()),
                bindparam(key="name", value=self.name, type_=sqlalchemy.String()),
                bindparam(
                    key="examples",
                    value=self.examples,
                    type_=sqlalchemy.JSON(),
                ),
                bindparam(
                    key="embedding_model",
                    value=global_config.default_model,
                    type_=sqlalchemy.String(),
                ),
            )
        )

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
            examples=self.examples,
        )

        await global_config.clients.qdrant.upsert(
            collection_name=self.org_code,
            points=Batch(
                ids=[random_flow_id.hex],
                vectors=description_embeddings,
            ),
        )

        now = datetime.datetime.now(tz=datetime.UTC)
        events.append(
            NewFormsRegistered(
                form_id=random_flow_id, registered_at=now, org_code=self.org_code
            )
        )
        return Response(register_at=now, form_id=random_flow_id)
