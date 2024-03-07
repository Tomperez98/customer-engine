from __future__ import annotations

import lego_workflows
import pytest

from customer_engine_api.config import resources
from customer_engine_api.core.whatsapp import check_same_hashed
from customer_engine_api.handlers.whatsapp import (
    delete_tokens,
    get_tokens,
    register_tokens,
    update_tokens,
)


@pytest.mark.e2e()
async def test_get_not_existing() -> None:
    with (
        resources.db_engine.begin() as conn,
        pytest.raises(get_tokens.WhatsappTokenNotFoundError),
    ):
        await lego_workflows.run_and_collect_events(
            cmd=get_tokens.Command(org_code="test", sql_conn=conn)
        )


@pytest.mark.e2e()
async def test_get_existing() -> None:
    org_code = "test"
    test_access_token = "EAAGu6e1JCZBkBOZB5PImmNsaabkZA3KiNVIBmwBixZA2YEui08ZBZAGEdeuJZBoU9s6D09yjjpociKauvfMWG2SZBTtMgvTGXG5ZAtsKza9SEzgo1RIefrpxAgFCUOjB5XGsmHlUeZBkTILECiiuX9dZAuiV9qZCQovPwlfvjrRGndbhr11MiCkFAjtzWEESVRJkuEFq7BSZCzGPW7qTuiG9hS5RqpBjXp53vU2Uw8IsEkyt8t5IZD"  # noqa: S105
    with resources.db_engine.begin() as conn:
        await lego_workflows.run_and_collect_events(
            register_tokens.Command(
                org_code=org_code,
                access_token=test_access_token,
                sql_conn=conn,
                user_token="HELLO",  # noqa: S106
                phone_number_id=123,
            )
        )
        whatsapp_token = (
            await lego_workflows.run_and_collect_events(
                cmd=get_tokens.Command(org_code=org_code, sql_conn=conn)
            )
        )[0].whatsapp_token

        assert whatsapp_token.org_code == org_code
        assert check_same_hashed(
            hashed=whatsapp_token.user_token, string="HELLO", algo="sha256"
        )
        assert whatsapp_token.phone_number_id == 123  # noqa: PLR2004
        assert (
            resources.fernet.decrypt(token=whatsapp_token.access_token).decode()
            == test_access_token
        )

        await lego_workflows.run_and_collect_events(
            cmd=delete_tokens.Command(org_code=org_code, sql_conn=conn)
        )
        with pytest.raises(get_tokens.WhatsappTokenNotFoundError):
            await lego_workflows.run_and_collect_events(
                cmd=get_tokens.Command(org_code=org_code, sql_conn=conn)
            )


async def test_update() -> None:
    org_code = "test"
    with resources.db_engine.begin() as conn:
        await lego_workflows.run_and_collect_events(
            register_tokens.Command(
                org_code=org_code,
                access_token="123",  # noqa: S106
                sql_conn=conn,
                user_token="HELLO",  # noqa: S106
                phone_number_id=123,
            )
        )
        await lego_workflows.run_and_collect_events(
            update_tokens.Command(
                org_code=org_code,
                new_access_token="567",  # noqa: S106
                new_user_token="BYE",  # noqa: S106
                sql_conn=conn,
                new_phone_number_id=457,
            )
        )
        whatsapp_token = (
            await lego_workflows.run_and_collect_events(
                get_tokens.Command(org_code=org_code, sql_conn=conn)
            )
        )[0].whatsapp_token
        assert whatsapp_token.org_code == org_code
        assert check_same_hashed(
            hashed=whatsapp_token.user_token, string="BYE", algo="sha256"
        )
        assert (
            resources.fernet.decrypt(token=whatsapp_token.access_token).decode()
            == "567"
        )
        assert whatsapp_token.phone_number_id == 457  # noqa: PLR2004
        await lego_workflows.run_and_collect_events(
            cmd=delete_tokens.Command(org_code=org_code, sql_conn=conn)
        )
