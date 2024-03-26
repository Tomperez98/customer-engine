from __future__ import annotations

import lego_workflows
import pytest

from customer_engine_api import handlers
from customer_engine_api.core.config import resources
from customer_engine_api.core.org_settings import OrgSettings


@pytest.mark.e2e()
async def test_get_not_existing() -> None:
    with resources.db_engine.begin() as conn:
        org_settings, _ = await lego_workflows.run_and_collect_events(
            cmd=handlers.org_settings.get_or_default.Command(
                org_code="test", sql_conn=conn
            )
        )
        assert org_settings.settings == OrgSettings(
            org_code="test",
            default_response="No response found for this prompt",
        )
        assert org_settings.is_default


async def test_update_not_existing() -> None:
    with resources.db_engine.begin() as conn:
        created_settings = (
            await lego_workflows.run_and_collect_events(
                cmd=handlers.org_settings.upsert.Command(
                    org_code="test",
                    default_response="Another response",
                    sql_conn=conn,
                )
            )
        )[0].settings

        assert created_settings == OrgSettings(
            org_code="test",
            default_response="Another response",
        )

        get_response, _ = await lego_workflows.run_and_collect_events(
            cmd=handlers.org_settings.get_or_default.Command(
                org_code="test", sql_conn=conn
            )
        )

        assert not get_response.is_default
        assert get_response.settings == OrgSettings(
            org_code="test",
            default_response="Another response",
        )

        await lego_workflows.run_and_collect_events(
            cmd=handlers.org_settings.delete.Command(org_code="test", sql_conn=conn)
        )

        get_response, _ = await lego_workflows.run_and_collect_events(
            cmd=handlers.org_settings.get_or_default.Command(
                org_code="test", sql_conn=conn
            )
        )

        assert get_response.is_default
