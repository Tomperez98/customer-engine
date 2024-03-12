"""Whatsapp core."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Self

import httpx
from mashumaro.mixins.orjson import DataClassORJSONMixin

from customer_engine_api.core.interfaces import SqlQueriable
from customer_engine_api.core.whatsapp import hashing

if TYPE_CHECKING:
    from cryptography.fernet import Fernet
    from sqlalchemy import Row

__all__ = ["hashing"]


class AsyncWhatsappClient:
    """Async whatsapp client to interact with API."""

    def __init__(self, bearer_token: str, phone_number_id: str) -> None:
        """Initialize a new instance."""
        self._client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {bearer_token}"},
            base_url=f"https://graph.facebook.com/v18.0/{phone_number_id}",
        )

    async def send_text_msg(self, text: str, to_wa_id: str) -> None:
        """Send text msg."""
        response = await self._client.post(
            url="/messages",
            json={
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to_wa_id,
                "type": "text",
                "text": {"preview_url": False, "body": text},
            },
        )
        response.raise_for_status()


@dataclass(frozen=False)
class WhatsappTokens(DataClassORJSONMixin, SqlQueriable):
    """Whatsapp token."""

    org_code: str
    access_token: str
    user_token: str

    @classmethod
    def from_row(cls: type[Self], row: Row[Any]) -> Self:
        """Instantiate class from sql row."""
        return cls.from_dict(row._asdict())

    def decrypt_access_token(self, fernet: Fernet) -> str:
        """Decrypt access token."""
        return fernet.decrypt(token=self.access_token).decode()
