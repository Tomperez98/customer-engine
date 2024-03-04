"""Whatsapp Tokens core."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal, Self, TypeAlias, assert_never

from mashumaro.mixins.orjson import DataClassORJSONMixin

from customer_engine_api.core.interfaces import SqlQueriable

if TYPE_CHECKING:
    from sqlalchemy import Row

HashAlgorithms: TypeAlias = Literal["sha256"]


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
