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

    def with_decrypted_access_token(self, fernet: Fernet) -> Self:
        """Decrypt access token."""
        self.access_token = fernet.decrypt(token=self.access_token).decode()
        return self
