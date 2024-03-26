"""Update org settings."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import lego_workflows
import sqlalchemy
from lego_workflows.components import (
    CommandComponent,
    DomainEvent,
    ResponseComponent,
)
from sqlalchemy import Connection, bindparam, text

from customer_engine_api.core.logging import logger
from customer_engine_api.handlers.org_settings import (
    get_or_default,
)

if TYPE_CHECKING:
    from customer_engine_api.core.org_settings import OrgSettings


@dataclass(frozen=True)
class OrgSettingUpdated(DomainEvent):  # noqa: D101
    org_code: str

    async def publish(self) -> None:  # noqa: D102
        logger.info(
            "Org settings updated for organization {org_code}",
            org_code=self.org_code,
        )


@dataclass(frozen=True)
class OrgSettingsCreated(DomainEvent):  # noqa: D101
    org_code: str

    async def publish(self) -> None:  # noqa: D102
        logger.info(
            "Org settings created for organization {org_code}", org_code=self.org_code
        )


@dataclass(frozen=True)
class Response(ResponseComponent):  # noqa: D101
    settings: OrgSettings


@dataclass(frozen=True)
class Command(CommandComponent[Response]):  # noqa: D101
    org_code: str
    default_response: str | None
    sql_conn: Connection

    async def run(self, events: list[DomainEvent]) -> Response:  # noqa: D102
        get_response, _ = await lego_workflows.run_and_collect_events(
            cmd=get_or_default.Command(org_code=self.org_code, sql_conn=self.sql_conn)
        )
        logger.debug(get_response)
        org_settings = get_response.settings.update(
            default_response=self.default_response,
        )

        if get_response.is_default:
            stmt = text(
                """
                INSERT INTO org_settings (
                    org_code,
                    default_response
                ) VALUES (
                    :org_code,
                    :default_response
                )
                """
            ).bindparams(
                bindparam(
                    key="org_code",
                    value=org_settings.org_code,
                    type_=sqlalchemy.String(),
                ),
                bindparam(
                    key="default_response",
                    value=org_settings.default_response,
                    type_=sqlalchemy.String(),
                ),
            )
            self.sql_conn.execute(stmt)
            events.append(OrgSettingsCreated(org_code=self.org_code))
        else:
            stmt = text("""
                        UPDATE org_settings
                        SET
                            default_response = :default_response
                        WHERE
                            org_code = :org_code
                        """).bindparams(
                bindparam(
                    key="org_code",
                    value=org_settings.org_code,
                    type_=sqlalchemy.String(),
                ),
                bindparam(
                    key="default_response",
                    value=org_settings.default_response,
                    type_=sqlalchemy.String(),
                ),
            )
            self.sql_conn.execute(stmt)
            events.append(OrgSettingUpdated(org_code=self.org_code))
        return Response(settings=org_settings)
