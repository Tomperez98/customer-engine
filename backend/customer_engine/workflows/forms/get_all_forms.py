"""Get all flows workflow."""
from __future__ import annotations

from dataclasses import dataclass

from lego_workflows.components import CommandComponent, DomainEvent, ResponseComponent
from sqlalchemy import Connection, text

from customer_engine.core.forms import Form


@dataclass(frozen=True)
class Response(ResponseComponent):
    """Get all whatsapp flows response data."""

    flows: list[Form]


@dataclass(frozen=True)
class Command(CommandComponent[Response, None]):
    """Get all whatsapp flows input data."""

    org_code: str
    conn: Connection

    async def run(
        self,
        events: list[DomainEvent],  # noqa: ARG002
    ) -> Response:
        """Execute get all whatsapp flows."""
        all_workflows = self.conn.execute(
            text(
                """
            SELECT
                org_code,
                form_id,
                name,
                description,
                embedding_model
            FROM forms
            WHERE org_code = :org_code"""
            ).bindparams(org_code=self.org_code)
        ).fetchall()

        return Response(
            flows=[Form.from_dict(workflow._asdict()) for workflow in all_workflows]
        )
