"""Configuration."""
from __future__ import annotations

import os

from sqlalchemy import Engine, create_engine


class _Config:
    def __init__(self) -> None:
        db_url = os.environ["DB_URL"]
        db_auth_token = os.environ["DB_AUTH_TOKEN"]
        self.db_engine: Engine = create_engine(
            url=f"sqlite+{db_url}/?authToken={db_auth_token}"
        )


global_config = _Config()
