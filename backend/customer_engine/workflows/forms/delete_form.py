"""Delete form workflow."""
from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import TYPE_CHECKING

from lego_workflows.components import CommandComponent, DomainEvent, ResponseComponent
from qdrant_client.http.models import PointIdsList
from sqlalchemy import Connection, TextClause, text

from customer_engine import logger
from customer_engine.core import global_config
from customer_engine.workflows.forms import get_form

if TYPE_CHECKING:
    from uuid import UUID


@dataclass(frozen=True)
class Response(ResponseComponent):
    """Response data to delete form workflow."""

    deleted_at: datetime.datetime


@dataclass(frozen=True)
class FormsHasBeenDeleted(DomainEvent):  # noqa: D101
    org_code: str
    form_id: UUID

    async def publish(self) -> None:  # noqa: D102
        logger.info(
            "Form {form_id} from organization {org_code} has been deleted.",
            form_id=self.form_id,
            org_code=self.org_code,
        )


@dataclass(frozen=True)
class Command(CommandComponent[Response, TextClause]):
    """Input data for delete form workflow."""

    form_id: UUID
    org_code: str
    conn: Connection

    async def run(self, events: list[DomainEvent]) -> Response:
        """Execute delete form workflow."""
        now = datetime.datetime.now(tz=datetime.UTC)

        await get_form.Command(
            form_id=self.form_id, org_code=self.org_code, conn=self.conn
        ).run(events=events)

        self.conn.execute(
            text(
                """
            DELETE FROM forms
            WHERE org_code = :org_code AND form_id = :form_id
        """
            ).bindparams(form_id=self.form_id, org_code=self.org_code)
        )
        self.conn.execute(
            text(
                """
            DELETE FROM form_configs
            WHERE org_code = :org_code AND form_id = :form_id
        """
            ).bindparams(form_id=self.form_id, org_code=self.org_code)
        )

        await global_config.clients.qdrant.delete(
            collection_name=self.org_code,
            points_selector=PointIdsList(points=[self.form_id.hex]),
        )

        events.append(FormsHasBeenDeleted(form_id=self.form_id, org_code=self.org_code))
        return Response(deleted_at=now)
