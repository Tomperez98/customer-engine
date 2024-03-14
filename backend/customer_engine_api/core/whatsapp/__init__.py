"""Whatsapp core."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Self

from mashumaro.mixins.orjson import DataClassORJSONMixin

from customer_engine_api.core.interfaces import SqlQueriable
from customer_engine_api.core.whatsapp import hashing

if TYPE_CHECKING:
    from cryptography.fernet import Fernet
    from sqlalchemy import Row

__all__ = ["hashing"]


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
