from __future__ import annotations

from uuid import UUID, uuid4

import lego_workflows
import pytest

from customer_engine_api import handlers
from customer_engine_api.core.automatic_responses import AutomaticResponse
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
                    examples=["This is an example"],
                    response="Text automated response",
                    sql_conn=conn,
                    qdrant_client=resources.clients.qdrant,
                    cohere_client=resources.clients.cohere,
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
                    qdrant_client=resources.clients.qdrant,
                )
            )


@pytest.mark.e2e()
async def test_search_by_prompt() -> None:
    with resources.db_engine.connect() as conn:
        test_org = "test"
        create_response, _ = await lego_workflows.run_and_collect_events(
            cmd=handlers.automatic_responses.create.Command(
                org_code=test_org,
                name="test automatic response",
                examples=["I'm a test case"],
                response="I know you are a test case",
                sql_conn=conn,
                qdrant_client=resources.clients.qdrant,
                cohere_client=resources.clients.cohere,
            )
        )

        search_by_prompt_response, _ = await lego_workflows.run_and_collect_events(
            cmd=handlers.automatic_responses.search_by_prompt.Command(
                org_code=test_org,
                prompt="I'm a test case",
                sql_conn=conn,
                qdrant_client=resources.clients.qdrant,
                cohere_client=resources.clients.cohere,
            )
        )

        assert isinstance(
            search_by_prompt_response.response_or_unmatched_prompt_id, AutomaticResponse
        )
        assert (
            search_by_prompt_response.response_or_unmatched_prompt_id.automatic_response_id
            == create_response.automatic_response_id
        )

        await lego_workflows.run_and_collect_events(
            cmd=handlers.automatic_responses.update.Command(
                org_code=test_org,
                automatic_response_id=create_response.automatic_response_id,
                new_name=None,
                new_examples=["I'm looking for a job"],
                new_response=None,
                sql_conn=conn,
                cohere_client=resources.clients.cohere,
                qdrant_client=resources.clients.qdrant,
            )
        )

        search_by_prompt_response, _ = await lego_workflows.run_and_collect_events(
            cmd=handlers.automatic_responses.search_by_prompt.Command(
                org_code=test_org,
                prompt="I'm a test case",
                sql_conn=conn,
                qdrant_client=resources.clients.qdrant,
                cohere_client=resources.clients.cohere,
            )
        )

        assert isinstance(
            search_by_prompt_response.response_or_unmatched_prompt_id, UUID
        )

        search_by_prompt_response, _ = await lego_workflows.run_and_collect_events(
            cmd=handlers.automatic_responses.search_by_prompt.Command(
                org_code=test_org,
                prompt="I'm looking for a job",
                sql_conn=conn,
                qdrant_client=resources.clients.qdrant,
                cohere_client=resources.clients.cohere,
            )
        )

        assert isinstance(
            search_by_prompt_response.response_or_unmatched_prompt_id, AutomaticResponse
        )
        assert (
            search_by_prompt_response.response_or_unmatched_prompt_id.name
            == "test automatic response"
        )
        assert (
            search_by_prompt_response.response_or_unmatched_prompt_id.response
            == "I know you are a test case"
        )

        await lego_workflows.run_and_collect_events(
            cmd=handlers.automatic_responses.delete.Command(
                org_code=test_org,
                automatic_response_id=create_response.automatic_response_id,
                sql_conn=conn,
                qdrant_client=resources.clients.qdrant,
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
                examples=["I'm a test case"],
                response="I know you are a test case",
                sql_conn=conn,
                qdrant_client=resources.clients.qdrant,
                cohere_client=resources.clients.cohere,
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

        update_response, _ = await lego_workflows.run_and_collect_events(
            cmd=handlers.automatic_responses.update.Command(
                org_code=test_org_code,
                automatic_response_id=create_response.automatic_response_id,
                sql_conn=conn,
                new_name="New name",
                new_response="New response",
                new_examples=None,
                cohere_client=resources.clients.cohere,
                qdrant_client=resources.clients.qdrant,
            )
        )

        assert not update_response.new_embeddings_calculated

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

        update_response, _ = await lego_workflows.run_and_collect_events(
            cmd=handlers.automatic_responses.update.Command(
                org_code=test_org_code,
                automatic_response_id=create_response.automatic_response_id,
                sql_conn=conn,
                new_name=None,
                new_response=None,
                new_examples=["New example"],
                cohere_client=resources.clients.cohere,
                qdrant_client=resources.clients.qdrant,
            )
        )

        assert update_response.new_embeddings_calculated

        updated_automatic_response = (
            await lego_workflows.run_and_collect_events(
                cmd=handlers.automatic_responses.get.Command(
                    org_code=test_org_code,
                    automatic_response_id=create_response.automatic_response_id,
                    sql_conn=conn,
                )
            )
        )[0].automatic_response

        assert updated_automatic_response.examples == ["New example"]

        await lego_workflows.run_and_collect_events(
            cmd=handlers.automatic_responses.delete.Command(
                org_code=test_org_code,
                automatic_response_id=create_response.automatic_response_id,
                sql_conn=conn,
                qdrant_client=resources.clients.qdrant,
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
                examples=["I'm a test case"],
                response="I know you are a test case",
                sql_conn=conn,
                qdrant_client=resources.clients.qdrant,
                cohere_client=resources.clients.cohere,
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
        assert get_response.automatic_response.examples == ["I'm a test case"]
        assert get_response.automatic_response.response == "I know you are a test case"

        await lego_workflows.run_and_collect_events(
            cmd=handlers.automatic_responses.delete.Command(
                org_code=test_org_code,
                automatic_response_id=create_response.automatic_response_id,
                sql_conn=conn,
                qdrant_client=resources.clients.qdrant,
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