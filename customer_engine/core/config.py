"""Configuration."""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import assert_never, cast

import loguru
from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine

from customer_engine.core.clients.open_ai import OpenAI
from customer_engine.typing import Environment

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
    openai: OpenAI


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

        self.clients = _Clients(openai=OpenAI(api_key=os.environ["OPEN_API_KEY"]))


global_config = _Config()
