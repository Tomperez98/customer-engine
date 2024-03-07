"""Whatsapp core."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal, Self, TypeAlias, assert_never

import httpx
from mashumaro.mixins.orjson import DataClassORJSONMixin

from customer_engine_api.core.interfaces import SqlQueriable

if TYPE_CHECKING:
    from cryptography.fernet import Fernet
    from sqlalchemy import Row

HashAlgorithms: TypeAlias = Literal["sha256"]


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


def hash_string(string: str, algo: HashAlgorithms) -> str:
    """Hash string."""
    hashed_string: str
    if algo == "sha256":
        hashed_string = hashlib.sha256(string.encode()).hexdigest()
    else:
        assert_never(algo)
    return hashed_string


def check_same_hashed(hashed: str, string: str, algo: HashAlgorithms) -> bool:
    """Check if user token is equal to class user token."""
    return hashed == hash_string(string=string, algo=algo)
