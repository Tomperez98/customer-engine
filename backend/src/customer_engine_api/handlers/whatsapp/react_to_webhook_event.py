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

from customer_engine_api.core import whatsapp
from customer_engine_api.core.api_clients.whatsapp import AsyncWhatsappClient
from customer_engine_api.handlers.automatic_responses import (
    get_auto_res_owns_example,
)
from customer_engine_api.handlers.org_settings import get_or_default
from customer_engine_api.handlers.whatsapp import get_tokens

if TYPE_CHECKING:
    import datetime

    import cohere
    from qdrant_client import AsyncQdrantClient
    from sqlalchemy import Connection

    from customer_engine_api.core.typing import JsonResponse


@dataclass(frozen=True)
class Response(ResponseComponent): ...


@dataclass(frozen=True)
class Command(CommandComponent[Response]):
    payload: JsonResponse
    org_code: str
    qdrant_client: AsyncQdrantClient
    cohere_client: cohere.AsyncClient
    sql_conn: Connection
    current_time: datetime.datetime

    async def run(self, events: list[DomainEvent]) -> Response:
        identified_payload = whatsapp.payloads.identify_payload(payload=self.payload)

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

        msg_to_send: str
        try:
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
                    current_time=self.current_time,
                )
            )

            events.extend(auto_res_events)

            msg_to_send = auto_res_response.automatic_response.response

        except get_auto_res_owns_example.UnableToMatchPromptWithAutomaticResponseError:
            (
                org_settings,
                get_or_default_events,
            ) = await lego_workflows.run_and_collect_events(
                cmd=get_or_default.Command(
                    org_code=self.org_code, sql_conn=self.sql_conn
                )
            )
            events.extend(get_or_default_events)
            msg_to_send = org_settings.settings.default_response

        await whatsapp_client.send_text_msg(
            text=msg_to_send,
            to_wa_id=identified_payload.wa_id,
        )

        return Response()
