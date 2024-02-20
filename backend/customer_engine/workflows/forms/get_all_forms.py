"""Get all flows workflow."""
from __future__ import annotations

from dataclasses import dataclass

import orjson
import sqlalchemy
from lego_workflows.components import CommandComponent, DomainEvent, ResponseComponent
from sqlalchemy import Connection, bindparam, text

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
                examples,
                embedding_model
            FROM forms
            WHERE org_code = :org_code"""
            ).bindparams(
                bindparam(
                    key="org_code", value=self.org_code, type_=sqlalchemy.String()
                )
            )
        ).fetchall()

        flows: list[Form] = []
        for workflow in all_workflows:
            workflow_data = workflow._asdict()
            workflow_data["examples"] = orjson.loads(workflow_data["examples"])
            flows.append(Form.from_dict(workflow_data))
        return Response(flows=flows)
