from __future__ import annotations

from uuid import UUID, uuid4

import lego_workflows
import pytest

from customer_engine_api import handlers
from customer_engine_api.core.automatic_responses import Example
from customer_engine_api.core.config import resources


@pytest.mark.e2e()
async def test_get_not_existing_example() -> None:
    with (
        resources.db_engine.begin() as conn,
        pytest.raises(handlers.automatic_responses.get_example.ExampleNotFoundError),
    ):
        await lego_workflows.run_and_collect_events(
            cmd=handlers.automatic_responses.get_example.Command(
                org_code="test",
                example_id=uuid4(),
                sql_conn=conn,
                automatic_response_id=None,
            )
        )


@pytest.mark.e2e()
async def test_list_examples() -> None:
    with (
        resources.db_engine.begin() as conn,
    ):
        test_org = "test"
        response_create_automatic, _ = await lego_workflows.run_and_collect_events(
            handlers.automatic_responses.create_auto_resp.Command(
                org_code=test_org,
                name="Example",
                response="Response",
                sql_conn=conn,
            )
        )

        examples_to_create = [f"Example {i}" for i in range(1, 3)]
        response_create_example, _ = await lego_workflows.run_and_collect_events(
            cmd=handlers.automatic_responses.create_example.Command(
                org_code=test_org,
                automatic_response_id=response_create_automatic.automatic_response_id,
                examples=examples_to_create,
                sql_conn=conn,
                qdrant_client=resources.clients.qdrant,
                cohere_client=resources.clients.cohere,
            )
        )
        created_examples: list[Example] = []
        for example_id, example_text in zip(
            response_create_example.example_ids, examples_to_create, strict=False
        ):
            created_examples.append(
                Example(
                    org_code=test_org,
                    automatic_response_id=response_create_automatic.automatic_response_id,
                    example=example_text,
                    example_id=example_id,
                )
            )

        list_examples_response, _ = await lego_workflows.run_and_collect_events(
            cmd=handlers.automatic_responses.list_examples.Command(
                org_code=test_org,
                automatic_response_id=response_create_automatic.automatic_response_id,
                sql_conn=conn,
            )
        )

        for example in list_examples_response.examples:
            assert example in created_examples

        get_all_examples, _ = await lego_workflows.run_and_collect_events(
            cmd=handlers.automatic_responses.get_bulk_examples.Command(
                org_code=test_org,
                examples_ids=[example.example_id for example in created_examples],
                sql_conn=conn,
            )
        )

        for example in get_all_examples.examples:
            assert example in created_examples

        await lego_workflows.run_and_collect_events(
            cmd=handlers.automatic_responses.delete_auto_res.Command(
                org_code=test_org,
                automatic_response_id=response_create_automatic.automatic_response_id,
                sql_conn=conn,
                qdrant_client=resources.clients.qdrant,
            )
        )

        for example in list_examples_response.examples:
            with pytest.raises(
                handlers.automatic_responses.get_example.ExampleNotFoundError
            ):
                await lego_workflows.run_and_collect_events(
                    handlers.automatic_responses.get_example.Command(
                        org_code=test_org,
                        example_id=example.example_id,
                        sql_conn=conn,
                        automatic_response_id=None,
                    )
                )


@pytest.mark.e2e()
async def test_update_example() -> None:
    with (
        resources.db_engine.begin() as conn,
    ):
        test_org = "test"
        response_create_automatic, _ = await lego_workflows.run_and_collect_events(
            handlers.automatic_responses.create_auto_resp.Command(
                org_code=test_org,
                name="Example",
                response="Response",
                sql_conn=conn,
            )
        )
        response_create_example, _ = await lego_workflows.run_and_collect_events(
            cmd=handlers.automatic_responses.create_example.Command(
                org_code=test_org,
                automatic_response_id=response_create_automatic.automatic_response_id,
                examples=["I'd like to order a pizza"],
                sql_conn=conn,
                qdrant_client=resources.clients.qdrant,
                cohere_client=resources.clients.cohere,
            )
        )

        response_update_example, _ = await lego_workflows.run_and_collect_events(
            handlers.automatic_responses.update_example.Command(
                org_code=test_org,
                automatic_response_id=response_create_automatic.automatic_response_id,
                example_id=response_create_example.example_ids[0],
                sql_conn=conn,
                qdrant_client=resources.clients.qdrant,
                cohere_client=resources.clients.cohere,
                example="I'd like to order food",
            )
        )

        assert (
            response_update_example.example.example_id
            == response_create_example.example_ids[0]
        )
        assert response_update_example.example.example == "I'd like to order food"
        similar_to_prompt_response, _ = await lego_workflows.run_and_collect_events(
            cmd=handlers.automatic_responses.similar_example_by_prompt.Command(
                org_code=test_org,
                prompt="I'd like to order food",
                qdrant_client=resources.clients.qdrant,
                cohere_client=resources.clients.cohere,
                sql_conn=conn,
            )
        )

        assert (
            similar_to_prompt_response.example.example_id
            == response_create_example.example_ids[0]
        )

        await lego_workflows.run_and_collect_events(
            cmd=handlers.automatic_responses.delete_auto_res.Command(
                org_code=test_org,
                sql_conn=conn,
                qdrant_client=resources.clients.qdrant,
                automatic_response_id=response_create_automatic.automatic_response_id,
            )
        )
        with pytest.raises(
            handlers.automatic_responses.get_example.ExampleNotFoundError
        ):
            await lego_workflows.run_and_collect_events(
                cmd=handlers.automatic_responses.get_example.Command(
                    org_code=test_org,
                    example_id=response_create_example.example_ids[0],
                    sql_conn=conn,
                    automatic_response_id=None,
                )
            )


@pytest.mark.e2e()
async def test_get_existing_example() -> None:
    with (
        resources.db_engine.begin() as conn,
    ):
        test_org = "test"
        response_create_automatic, _ = await lego_workflows.run_and_collect_events(
            handlers.automatic_responses.create_auto_resp.Command(
                org_code=test_org,
                name="Example",
                response="Response",
                sql_conn=conn,
            )
        )

        create_example_command = handlers.automatic_responses.create_example.Command(
            org_code=test_org,
            automatic_response_id=response_create_automatic.automatic_response_id,
            examples=["I'd like to order a pizza"],
            sql_conn=conn,
            qdrant_client=resources.clients.qdrant,
            cohere_client=resources.clients.cohere,
        )

        await create_example_command._upsert_example(example_ids=[uuid4()])  # noqa: SLF001

        response_create_example, _ = await lego_workflows.run_and_collect_events(
            cmd=create_example_command
        )
        get_example_response, _ = await lego_workflows.run_and_collect_events(
            cmd=handlers.automatic_responses.get_example.Command(
                org_code=test_org,
                example_id=response_create_example.example_ids[0],
                sql_conn=conn,
                automatic_response_id=response_create_automatic.automatic_response_id,
            )
        )
        assert (
            get_example_response.example.automatic_response_id
            == response_create_automatic.automatic_response_id
        )
        assert (
            get_example_response.example.example_id
            == response_create_example.example_ids[0]
        )

        similar_to_prompt_response, _ = await lego_workflows.run_and_collect_events(
            cmd=handlers.automatic_responses.similar_example_by_prompt.Command(
                org_code=test_org,
                prompt="I want to order a pizza",
                qdrant_client=resources.clients.qdrant,
                cohere_client=resources.clients.cohere,
                sql_conn=conn,
            )
        )

        assert (
            similar_to_prompt_response.example.automatic_response_id
            == get_example_response.example.automatic_response_id
        )
        assert (
            similar_to_prompt_response.example.example_id
            == get_example_response.example.example_id
        )

        response_owner_auto_res, _ = await lego_workflows.run_and_collect_events(
            handlers.automatic_responses.get_auto_res_owns_example.Command(
                org_code=test_org,
                example_id_or_prompt=similar_to_prompt_response.example.example_id,
                qdrant_client=resources.clients.qdrant,
                cohere_client=resources.clients.cohere,
                sql_conn=conn,
            )
        )

        assert (
            response_owner_auto_res.automatic_response.automatic_response_id
            == response_create_automatic.automatic_response_id
        )
        await lego_workflows.run_and_collect_events(
            cmd=handlers.automatic_responses.delete_example.Command(
                org_code=test_org,
                example_id=response_create_example.example_ids[0],
                sql_conn=conn,
                qdrant_client=resources.clients.qdrant,
                automatic_response_id=response_create_automatic.automatic_response_id,
            )
        )
        with pytest.raises(
            handlers.automatic_responses.get_example.ExampleNotFoundError
        ):
            await lego_workflows.run_and_collect_events(
                cmd=handlers.automatic_responses.get_example.Command(
                    org_code=test_org,
                    example_id=response_create_example.example_ids[0],
                    sql_conn=conn,
                    automatic_response_id=response_create_automatic.automatic_response_id,
                )
            )

        await lego_workflows.run_and_collect_events(
            handlers.automatic_responses.delete_auto_res.Command(
                org_code=test_org,
                automatic_response_id=response_create_automatic.automatic_response_id,
                sql_conn=conn,
                qdrant_client=resources.clients.qdrant,
            )
        )


@pytest.mark.e2e()
async def test_get_not_existing_automatic_response() -> None:
    with (
        resources.db_engine.connect() as conn,
        pytest.raises(
            handlers.automatic_responses.get_auto_res.AutomaticResponseNotFoundError
        ),
    ):
        await lego_workflows.run_and_collect_events(
            cmd=handlers.automatic_responses.get_auto_res.Command(
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
                cmd=handlers.automatic_responses.create_auto_resp.Command(
                    org_code="test",
                    name=name_to_use,
                    response="Text automated response",
                    sql_conn=conn,
                )
            )
            created_automated_responses.add(created_response.automatic_response_id)

        list_response, _ = await lego_workflows.run_and_collect_events(
            handlers.automatic_responses.list_auto_res.Command(
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
                handlers.automatic_responses.delete_auto_res.Command(
                    org_code="test",
                    automatic_response_id=created_auto_response,
                    sql_conn=conn,
                    qdrant_client=resources.clients.qdrant,
                )
            )


@pytest.mark.e2e()
async def test_update_automatic_response() -> None:
    with resources.db_engine.connect() as conn:
        test_org_code = "test"
        create_response, _ = await lego_workflows.run_and_collect_events(
            cmd=handlers.automatic_responses.create_auto_resp.Command(
                org_code=test_org_code,
                name="test automatic response",
                response="I know you are a test case",
                sql_conn=conn,
            )
        )

        get_response, _ = await lego_workflows.run_and_collect_events(
            cmd=handlers.automatic_responses.get_auto_res.Command(
                org_code=test_org_code,
                automatic_response_id=create_response.automatic_response_id,
                sql_conn=conn,
            )
        )

        assert get_response.automatic_response.name == "test automatic response"
        assert get_response.automatic_response.response == "I know you are a test case"

        await lego_workflows.run_and_collect_events(
            cmd=handlers.automatic_responses.update_auto_res.Command(
                org_code=test_org_code,
                automatic_response_id=create_response.automatic_response_id,
                sql_conn=conn,
                new_name="New name",
                new_response="New response",
            )
        )

        updated_automatic_response = (
            await lego_workflows.run_and_collect_events(
                cmd=handlers.automatic_responses.get_auto_res.Command(
                    org_code=test_org_code,
                    automatic_response_id=create_response.automatic_response_id,
                    sql_conn=conn,
                )
            )
        )[0].automatic_response

        assert updated_automatic_response.name == "New name"
        assert updated_automatic_response.response == "New response"

        await lego_workflows.run_and_collect_events(
            cmd=handlers.automatic_responses.delete_auto_res.Command(
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
            cmd=handlers.automatic_responses.create_auto_resp.Command(
                org_code=test_org_code,
                name="test automatic response",
                response="I know you are a test case",
                sql_conn=conn,
            )
        )

        get_response, _ = await lego_workflows.run_and_collect_events(
            cmd=handlers.automatic_responses.get_auto_res.Command(
                org_code=test_org_code,
                automatic_response_id=create_response.automatic_response_id,
                sql_conn=conn,
            )
        )
        assert get_response.automatic_response.name == "test automatic response"

        assert get_response.automatic_response.response == "I know you are a test case"

        await lego_workflows.run_and_collect_events(
            cmd=handlers.automatic_responses.delete_auto_res.Command(
                org_code=test_org_code,
                automatic_response_id=create_response.automatic_response_id,
                sql_conn=conn,
                qdrant_client=resources.clients.qdrant,
            )
        )

        with pytest.raises(
            handlers.automatic_responses.get_auto_res.AutomaticResponseNotFoundError
        ):
            await lego_workflows.run_and_collect_events(
                cmd=handlers.automatic_responses.get_auto_res.Command(
                    org_code=test_org_code,
                    automatic_response_id=create_response.automatic_response_id,
                    sql_conn=conn,
                )
            )
