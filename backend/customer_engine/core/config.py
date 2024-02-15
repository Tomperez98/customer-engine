"""Configuration."""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING, assert_never, cast

import cohere
import loguru
from dotenv import load_dotenv
from qdrant_client import AsyncQdrantClient
from sqlalchemy import Engine, create_engine

from customer_engine.typing import Environment

if TYPE_CHECKING:
    from customer_engine.core.whatsapp_flows import CohereModels

load_dotenv(dotenv_path=".env")


def _configure_logger(logger: loguru.Logger, level: str) -> loguru.Logger:
    """Configure logger for the system."""
    logger.remove()
    fmt = "{time:HH:mm:ss} <lvl>[{level}]</lvl> {message} <green>{name}:{function}:{line}</green>"
    logger.add(sys.stderr, format=fmt, level=level)
    return logger


logger = _configure_logger(logger=loguru.logger, level=os.environ["LOG_LEVEL"])


@dataclass(frozen=True)
class _Clients:
    qdrant: AsyncQdrantClient
    cohere: cohere.AsyncClient


class _Config:
    def __init__(self) -> None:
        db_url = os.environ["DB_URL"]
        db_auth_token = os.environ["DB_AUTH_TOKEN"]
        environment = cast(Environment, os.environ["ENVIRONMENT"])

        self.db_engine: Engine
        if environment == "development":
            self.db_engine = create_engine(
                url=f"sqlite+{db_url}/?authToken={db_auth_token}", echo=True
            )
        elif environment == "production":
            self.db_engine = create_engine(
                url=f"sqlite+{db_url}/?authToken={db_auth_token}", echo=False
            )
        else:
            assert_never(environment)

        qdrant_url = os.environ["QDRANT_URL"]
        self.clients = _Clients(
            qdrant=AsyncQdrantClient(
                url=f"{qdrant_url}:6333", api_key=os.environ["QDRANT_API_KEY"]
            ),
            cohere=cohere.AsyncClient(api_key=os.environ["COHERE_API_KEY"]),
        )
        self.default_org = "default"
        self.default_model: CohereModels = "embed-multilingual-light-v3.0"


global_config = _Config()
