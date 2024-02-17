"""Get flow workflow."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from lego_workflows.components import (
    CommandComponent,
    DomainError,
    DomainEvent,
    ResponseComponent,
)
from mashumaro.codecs.orjson import ORJSONDecoder
from sqlalchemy import Connection, text

from customer_engine.core.forms import Form, FormConfig

if TYPE_CHECKING:
    from uuid import UUID


class FormNotFoundError(DomainError):
    """Raised when whatsapp flow does not exists."""

    def __init__(self, form_id: UUID, org_code: str) -> None:  # noqa: D107
        super().__init__(f"Whatsapp flow {form_id} from org {org_code} not found.")


class NoFormConfigurationFoundError(DomainError):
    """Raised when form configuration does not exists."""

    def __init__(self, form_id: UUID, org_code: str) -> None:  # noqa: D107
        super().__init__(f"Form configuration {form_id} from org {org_code} not found.")


@dataclass(frozen=True)
class Response(ResponseComponent):
    """Response data for get flow workflow."""

    form: Form
    configuration: FormConfig


@dataclass(frozen=True)
class Command(CommandComponent[Response, None]):
    """Input data for get flow workflow."""

    org_code: str
    form_id: UUID
    conn: Connection

    async def run(
        self,
        events: list[DomainEvent],  # noqa: ARG002
    ) -> Response:
        """Execute get flow workflow."""
        whatsapp_flow = self.conn.execute(
            text(
                """
            SELECT
                org_code,
                form_id,
                name,
                description,
                embedding_model
            FROM forms
            WHERE org_code = :org_code AND form_id = :form_id
            """
            ).bindparams(form_id=self.form_id, org_code=self.org_code)
        ).fetchone()
        if whatsapp_flow is None:
            raise FormNotFoundError(form_id=self.form_id, org_code=self.org_code)

        form_configuration = self.conn.execute(
            text(
                """
            SELECT
                configuration
            FROM form_configs
            WHERE org_code = :org_code AND form_id = :form_id
            """
            ).bindparams(form_id=self.form_id, org_code=self.org_code)
        ).fetchone()
        if form_configuration is None:
            raise NoFormConfigurationFoundError(
                form_id=self.form_id, org_code=self.org_code
            )

        existing_form = Form.from_dict(whatsapp_flow._asdict())

        return Response(
            form=existing_form,
            configuration=ORJSONDecoder(FormConfig).decode(
                form_configuration._asdict()["configuration"]
            ),
        )
