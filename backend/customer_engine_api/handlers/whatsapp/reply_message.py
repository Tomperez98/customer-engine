"""
Reply to message.

https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks/payload-examples
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, assert_never
from uuid import UUID

import lego_workflows
from lego_workflows.components import CommandComponent, DomainEvent, ResponseComponent
from result import Ok

from customer_engine_api.core import whatsapp
from customer_engine_api.core.api_clients.whatsapp import AsyncWhatsappClient
from customer_engine_api.core.automatic_responses import AutomaticResponse
from customer_engine_api.handlers.automatic_responses import search_by_prompt
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
    org_code: str
    received_msg: JsonResponse
    sql_conn: Connection
    cohere_client: cohere.AsyncClient
    qdrant_client: AsyncQdrantClient

    async def run(self, events: list[DomainEvent]) -> Response:  # noqa: D102
        identified_payload_or_err = whatsapp.payloads.identify_payload(
            payload=self.received_msg
        )
        if not isinstance(identified_payload_or_err, Ok):
            raise identified_payload_or_err.err()

        identified_payload = identified_payload_or_err.unwrap()

        (
            search_by_prompt_response,
            search_by_prompt_events,
        ) = await lego_workflows.run_and_collect_events(
            cmd=search_by_prompt.Command(
                org_code=self.org_code,
                prompt=identified_payload.text,
                sql_conn=self.sql_conn,
                cohere_client=self.cohere_client,
                qdrant_client=self.qdrant_client,
            )
        )
        events.extend(search_by_prompt_events)
        wa_token_response = (
            await lego_workflows.run_and_collect_events(
                cmd=get_tokens.Command(org_code=self.org_code, sql_conn=self.sql_conn)
            )
        )[0]

        whatsapp_client = AsyncWhatsappClient(
            bearer_token=wa_token_response.whatsapp_token.access_token,
            phone_number_id=identified_payload.phone_number_id,
        )

        if isinstance(
            search_by_prompt_response.response_or_unmatched_prompt_id, AutomaticResponse
        ):
            await whatsapp_client.send_text_msg(
                text=search_by_prompt_response.response_or_unmatched_prompt_id.response,
                to_wa_id=identified_payload.wa_id,
            )

        elif isinstance(
            search_by_prompt_response.response_or_unmatched_prompt_id, UUID
        ):
            await whatsapp_client.send_text_msg(
                text="No response found for this prompt",
                to_wa_id=identified_payload.wa_id,
            )
        else:
            assert_never(search_by_prompt_response.response_or_unmatched_prompt_id)
        return Response()
