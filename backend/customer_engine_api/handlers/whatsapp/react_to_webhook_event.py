"""React to webhook event."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import lego_workflows
from lego_workflows.components import (
    CommandComponent,
    DomainEvent,
    ResponseComponent,
)
from result import Err

from customer_engine_api.core import whatsapp
from customer_engine_api.core.api_clients.whatsapp import AsyncWhatsappClient
from customer_engine_api.handlers.automatic_responses import (
    get_auto_res_owns_example,
)
from customer_engine_api.handlers.whatsapp import get_tokens

if TYPE_CHECKING:
    import cohere
    from qdrant_client import AsyncQdrantClient
    from sqlalchemy import Connection

    from customer_engine_api.core.typing import JsonResponse


@dataclass(frozen=True)
class Response(ResponseComponent): ...  # noqa: D101


@dataclass(frozen=True)
class Command(CommandComponent[Response]):  # noqa: D101
    payload: JsonResponse
    org_code: str
    qdrant_client: AsyncQdrantClient
    cohere_client: cohere.AsyncClient
    sql_conn: Connection

    async def run(self, events: list[DomainEvent]) -> Response:  # noqa: D102
        identified_payload_or_err = whatsapp.payloads.identify_payload(
            payload=self.payload
        )
        if isinstance(identified_payload_or_err, Err):
            raise identified_payload_or_err.err()
        identified_payload = identified_payload_or_err.unwrap()

        (
            auto_res_response,
            auto_res_events,
        ) = await lego_workflows.run_and_collect_events(
            cmd=get_auto_res_owns_example.Command(
                org_code=self.org_code,
                example_id_or_prompt=identified_payload.text,
                qdrant_client=self.qdrant_client,
                cohere_client=self.cohere_client,
                sql_conn=self.sql_conn,
            )
        )

        events.extend(auto_res_events)

        (
            get_tokens_response,
            get_tokens_events,
        ) = await lego_workflows.run_and_collect_events(
            get_tokens.Command(org_code=self.org_code, sql_conn=self.sql_conn)
        )

        events.extend(get_tokens_events)

        whatsapp_client = AsyncWhatsappClient(
            bearer_token=get_tokens_response.whatsapp_token.access_token,
            phone_number_id=identified_payload.phone_number_id,
        )
        await whatsapp_client.send_text_msg(
            text=auto_res_response.automatic_response.response,
            to_wa_id=identified_payload.wa_id,
        )

        return Response()
