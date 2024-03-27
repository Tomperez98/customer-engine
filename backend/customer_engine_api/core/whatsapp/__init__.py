"""Whatsapp core."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Self

from mashumaro.mixins.orjson import DataClassORJSONMixin

from customer_engine_api.core.interfaces import SqlQueriable
from customer_engine_api.core.whatsapp import _hashing as hashing, _payloads as payloads

if TYPE_CHECKING:
    from cryptography.fernet import Fernet
    from sqlalchemy import Row

__all__ = ["hashing", "payloads"]


@dataclass(frozen=True)
class WhatsappTokens(DataClassORJSONMixin, SqlQueriable):
    """Whatsapp token."""

    org_code: str
    access_token: str
    user_token: str

    @classmethod
    def from_row(cls: type[Self], row: Row[Any]) -> Self:
        """Instantiate class from sql row."""
        return cls.from_dict(row._asdict())

    def with_decrypted_access_token(self, fernet: Fernet) -> WhatsappTokens:
        """Decrypt access token."""
        return WhatsappTokens(
            org_code=self.org_code,
            access_token=fernet.decrypt(token=self.access_token).decode(),
            user_token=self.user_token,
        )

    def update(
        self, access_token: str | None, user_token: str | None, fernet: Fernet
    ) -> WhatsappTokens:
        """Update entity."""
        return WhatsappTokens(
            org_code=self.org_code,
            access_token=fernet.encrypt(access_token.encode()).decode()
            if access_token is not None
            else self.access_token,
            user_token=hashing.hash_string(string=user_token, algo="sha256")
            if user_token is not None
            else self.user_token,
        )
