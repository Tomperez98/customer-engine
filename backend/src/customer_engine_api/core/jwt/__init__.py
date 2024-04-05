"""JWT module."""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field

import jwt
from mashumaro import field_options
from mashumaro.mixins.orjson import DataClassORJSONMixin


@dataclass(frozen=True)
class KindeToken(DataClassORJSONMixin):
    """Kinde token."""

    token_id: str = field(metadata=field_options(alias="jti"))
    scopes: list[str] = field(metadata=field_options(alias="scp"))
    subject: str = field(metadata=field_options(alias="sub"))
    org_code: str
    expiration_time: int = field(metadata=field_options(alias="exp"))

    def is_expired(self, current_time: datetime.datetime) -> bool:
        """Check if token is expired."""
        return current_time > datetime.datetime.fromtimestamp(
            self.expiration_time, tz=datetime.UTC
        )


def decode_token(encoded_token: str) -> KindeToken:
    """Decode JWT token."""
    return KindeToken.from_dict(
        jwt.decode(
            encoded_token,
            options={"verify_signature": False},
            algorithms=[jwt.get_unverified_header(encoded_token)["alg"]],
        )
    )