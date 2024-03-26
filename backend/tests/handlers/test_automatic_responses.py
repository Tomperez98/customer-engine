from __future__ import annotations

from uuid import UUID, uuid4

import lego_workflows
import pytest

from customer_engine_api import handlers
from customer_engine_api.core.config import resources


@pytest.mark.e2e()
async def test_get_not_existing_automatic_response() -> None:
    with (
        resources.db_engine.connect() as conn,
        pytest.raises(handlers.automatic_responses.get.AutomaticResponseNotFoundError),
    ):
        await lego_workflows.run_and_collect_events(
            cmd=handlers.automatic_responses.get.Command(
                org_code="test", automatic_response_id=uuid4(), sql_conn=conn
            )
        )


@pytest.mark.e2e()
async def test_list_org_automated_responses() -> None:
    with resources.db_engine.connect() as conn:
        created_automated_responses: set[UUID] = set()
        for i in range(2):
            name_to_use = f"Automatic response {i}"

            created_response, _ = await lego_workflows.run_and_collect_events(
                cmd=handlers.automatic_responses.create.Command(
                    org_code="test",
                    name=name_to_use,
                    response="Text automated response",
                    sql_conn=conn,
                )
            )
            created_automated_responses.add(created_response.automatic_response_id)

        list_response, _ = await lego_workflows.run_and_collect_events(
            handlers.automatic_responses.list_all.Command(
                org_code="test", sql_conn=conn
            )
        )

        ids_for_listed: set[UUID] = {
            automated_response.automatic_response_id
            for automated_response in list_response.automatic_responses
        }
        assert created_automated_responses.issubset(ids_for_listed)

        for created_auto_response in created_automated_responses:
            await lego_workflows.run_and_collect_events(
                handlers.automatic_responses.delete.Command(
                    org_code="test",
                    automatic_response_id=created_auto_response,
                    sql_conn=conn,
                )
            )


@pytest.mark.e2e()
async def test_update_automatic_response() -> None:
    with resources.db_engine.connect() as conn:
        test_org_code = "test"
        create_response, _ = await lego_workflows.run_and_collect_events(
            cmd=handlers.automatic_responses.create.Command(
                org_code=test_org_code,
                name="test automatic response",
                response="I know you are a test case",
                sql_conn=conn,
            )
        )

        get_response, _ = await lego_workflows.run_and_collect_events(
            cmd=handlers.automatic_responses.get.Command(
                org_code=test_org_code,
                automatic_response_id=create_response.automatic_response_id,
                sql_conn=conn,
            )
        )

        assert get_response.automatic_response.name == "test automatic response"
        assert get_response.automatic_response.response == "I know you are a test case"

        await lego_workflows.run_and_collect_events(
            cmd=handlers.automatic_responses.update.Command(
                org_code=test_org_code,
                automatic_response_id=create_response.automatic_response_id,
                sql_conn=conn,
                new_name="New name",
                new_response="New response",
            )
        )

        updated_automatic_response = (
            await lego_workflows.run_and_collect_events(
                cmd=handlers.automatic_responses.get.Command(
                    org_code=test_org_code,
                    automatic_response_id=create_response.automatic_response_id,
                    sql_conn=conn,
                )
            )
        )[0].automatic_response

        assert updated_automatic_response.name == "New name"
        assert updated_automatic_response.response == "New response"

        await lego_workflows.run_and_collect_events(
            cmd=handlers.automatic_responses.delete.Command(
                org_code=test_org_code,
                automatic_response_id=create_response.automatic_response_id,
                sql_conn=conn,
            )
        )


@pytest.mark.e2e()
async def test_get_existing_automatic_response() -> None:
    with resources.db_engine.connect() as conn:
        test_org_code = "test"
        create_response, _ = await lego_workflows.run_and_collect_events(
            cmd=handlers.automatic_responses.create.Command(
                org_code=test_org_code,
                name="test automatic response",
                response="I know you are a test case",
                sql_conn=conn,
            )
        )

        get_response, _ = await lego_workflows.run_and_collect_events(
            cmd=handlers.automatic_responses.get.Command(
                org_code=test_org_code,
                automatic_response_id=create_response.automatic_response_id,
                sql_conn=conn,
            )
        )
        assert get_response.automatic_response.name == "test automatic response"

        assert get_response.automatic_response.response == "I know you are a test case"

        await lego_workflows.run_and_collect_events(
            cmd=handlers.automatic_responses.delete.Command(
                org_code=test_org_code,
                automatic_response_id=create_response.automatic_response_id,
                sql_conn=conn,
            )
        )

        with pytest.raises(
            handlers.automatic_responses.get.AutomaticResponseNotFoundError
        ):
            await lego_workflows.run_and_collect_events(
                cmd=handlers.automatic_responses.get.Command(
                    org_code=test_org_code,
                    automatic_response_id=create_response.automatic_response_id,
                    sql_conn=conn,
                )
            )
