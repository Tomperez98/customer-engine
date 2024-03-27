"""Whatsapp API client."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

from customer_engine_api.core import http

if TYPE_CHECKING:
    from customer_engine_api.core.typing import JsonResponse


class AsyncWhatsappClient:
    """Async whatsapp client to interact with API."""

    def __init__(self, bearer_token: str, phone_number_id: str) -> None:
        """Initialize a new instance."""
        self._client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {bearer_token}"},
            base_url=f"https://graph.facebook.com/v18.0/{phone_number_id}",
            transport=httpx.AsyncHTTPTransport(retries=3),
        )

    async def send_text_msg(self, text: str, to_wa_id: str) -> JsonResponse:
        """Send text msg."""
        return http.safe_return(
            await self._client.post(
                url="/messages",
                json={
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": to_wa_id,
                    "type": "text",
                    "text": {"preview_url": False, "body": text},
                },
            )
        )
