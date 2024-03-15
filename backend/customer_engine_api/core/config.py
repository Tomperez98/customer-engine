"""Configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import assert_never, cast

import cohere
from cryptography.fernet import Fernet
from fastapi.templating import Jinja2Templates
from qdrant_client import AsyncQdrantClient
from sqlalchemy import create_engine

from customer_engine_api.core.typing import Environment


@dataclass(frozen=True)
class _Clients:
    qdrant: AsyncQdrantClient
    cohere: cohere.AsyncClient


class _Resources:
    def __init__(self) -> None:
        db_url = os.environ["DB_URL"]
        db_auth_token = os.environ["DB_AUTH_TOKEN"]
        environment = cast(Environment, os.environ["ENVIRONMENT"])

        echo_db: bool
        if environment == "development":
            echo_db = True
        elif environment == "staging":
            echo_db = False

        else:
            assert_never(environment)

        self.db_engine = create_engine(
            url=f"sqlite+{db_url}/?authToken={db_auth_token}",
            echo=echo_db,
            pool_pre_ping=True,
            connect_args={"timeout": 60},
        )

        qdrant_url = os.environ["QDRANT_URL"]
        self.clients = _Clients(
            qdrant=AsyncQdrantClient(
                url=f"{qdrant_url}:6333", api_key=os.environ["QDRANT_API_KEY"]
            ),
            cohere=cohere.AsyncClient(api_key=os.environ["COHERE_API_KEY"]),
        )
        self.fernet: Fernet = Fernet(key=os.environ["ENCRYPT_KEY"])
        self.templates = Jinja2Templates("templates")


resources = _Resources()
