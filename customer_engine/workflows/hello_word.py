from __future__ import annotations

import datetime
from dataclasses import dataclass

import sqlalchemy
from lego_workflows.components import Command, DomainEvent, Response
from sqlalchemy import TextClause

from customer_engine.core import global_config


@dataclass(frozen=True)
class HelloWorldResponse(Response):
    greet_at: datetime.datetime


class HelloWorld(Command[Response, TextClause]):
    name: str
    age: int

    async def run(
        self, state_changes: list[TextClause], events: list[DomainEvent]
    ) -> Response:
        with global_config.db_engine.connect() as conn:
            conn.execute(sqlalchemy.text("SELECT 1"))
        return HelloWorldResponse(greet_at=datetime.datetime.now(tz=datetime.UTC))
