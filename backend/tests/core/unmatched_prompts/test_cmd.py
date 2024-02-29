from __future__ import annotations

from uuid import UUID, uuid4

import lego_workflows
import pytest

from customer_engine_api.config import resources
from customer_engine_api.core import automatic_responses, unmatched_prompts


@pytest.mark.e2e()
async def test_list_unmatched_prompts() -> None:
    with resources.db_engine.begin() as conn:
        created_umatched_prompts: set[UUID] = set()
        for i in range(2):
            prompt_used = f"Unmatched prompt {i}"

            created, _ = await lego_workflows.run_and_collect_events(
                unmatched_prompts.cmd.register.Command(
                    org_code="test",
                    prompt=prompt_used,
                    sql_conn=conn,
                )
            )

            created_umatched_prompts.add(created.prompt_id)

        listed_umatched_promts, _ = await lego_workflows.run_and_collect_events(
            cmd=unmatched_prompts.cmd.list.Command(org_code="test", sql_conn=conn)
        )

        ids_for_listed: set[UUID] = {
            unmatched_prompt.prompt_id
            for unmatched_prompt in listed_umatched_promts.unmatched_prompts
        }

        assert created_umatched_prompts.issubset(ids_for_listed)

        for prompt_id in created_umatched_prompts:
            await lego_workflows.run_and_collect_events(
                cmd=unmatched_prompts.cmd.delete.Command(
                    org_code="test", prompt_id=prompt_id, sql_conn=conn
                )
            )


@pytest.mark.e2e()
async def test_get_not_existing() -> None:
    with resources.db_engine.begin() as conn, pytest.raises(
        unmatched_prompts.cmd.get.UnmatchedResponseNotFoundError
    ):
        await lego_workflows.run_and_collect_events(
            cmd=unmatched_prompts.cmd.get.Command(
                org_code="test", prompt_id=uuid4(), sql_conn=conn
            )
        )


@pytest.mark.e2e()
async def test_get_existing() -> None:
    with resources.db_engine.begin() as conn:
        created, _ = await lego_workflows.run_and_collect_events(
            unmatched_prompts.cmd.register.Command(
                org_code="test",
                prompt="Soy un unmatched prompt.",
                sql_conn=conn,
            )
        )
        existing, _ = await lego_workflows.run_and_collect_events(
            cmd=unmatched_prompts.cmd.get.Command(
                org_code="test", prompt_id=created.prompt_id, sql_conn=conn
            )
        )
        assert existing.unmatched_prompt.prompt_id == created.prompt_id
        assert existing.unmatched_prompt.org_code == "test"
        assert existing.unmatched_prompt.prompt == "Soy un unmatched prompt."

        deleted, _ = await lego_workflows.run_and_collect_events(
            cmd=unmatched_prompts.cmd.delete.Command(
                org_code="test", prompt_id=created.prompt_id, sql_conn=conn
            )
        )
        with pytest.raises(unmatched_prompts.cmd.get.UnmatchedResponseNotFoundError):
            await lego_workflows.run_and_collect_events(
                cmd=unmatched_prompts.cmd.get.Command(
                    org_code="test", prompt_id=deleted.prompt_id, sql_conn=conn
                )
            )


@pytest.mark.e2e()
async def test_add_unmatched_as_example() -> None:
    org_code = "test"
    with resources.db_engine.begin() as conn:
        created_automatic_response, _ = await lego_workflows.run_and_collect_events(
            cmd=automatic_responses.cmd.create.Command(
                org_code=org_code,
                name="Trabajos",
                examples=["abc"],
                response="Link lever",
                sql_conn=conn,
                qdrant_client=resources.clients.qdrant,
                cohere_client=resources.clients.cohere,
            )
        )

        created_unmatched_prompt, _ = await lego_workflows.run_and_collect_events(
            unmatched_prompts.cmd.register.Command(
                org_code=org_code,
                prompt="Me gustaria trabajar con usteded",
                sql_conn=conn,
            )
        )

        unmatched_prompt, _ = await lego_workflows.run_and_collect_events(
            cmd=unmatched_prompts.cmd.add_as_example_to_automatic_response.Command(
                org_code=org_code,
                prompt_id=created_unmatched_prompt.prompt_id,
                autoamtic_response_id=created_automatic_response.automatic_response_id,
                sql_conn=conn,
                cohere_client=resources.clients.cohere,
                qdrant_client=resources.clients.qdrant,
            )
        )

        with pytest.raises(unmatched_prompts.cmd.get.UnmatchedResponseNotFoundError):
            await lego_workflows.run_and_collect_events(
                cmd=unmatched_prompts.cmd.get.Command(
                    org_code=org_code,
                    prompt_id=unmatched_prompt.prompt_id,
                    sql_conn=conn,
                )
            )

        modified_automatic_response, _ = await lego_workflows.run_and_collect_events(
            cmd=automatic_responses.cmd.get.Command(
                org_code=org_code,
                automatic_response_id=created_automatic_response.automatic_response_id,
                sql_conn=conn,
            )
        )

        assert (
            modified_automatic_response.automatic_response.examples[-1]
            == "Me gustaria trabajar con usteded"
        )

        await lego_workflows.run_and_collect_events(
            cmd=automatic_responses.cmd.delete.Command(
                org_code=org_code,
                automatic_response_id=created_automatic_response.automatic_response_id,
                sql_conn=conn,
                qdrant_client=resources.clients.qdrant,
            )
        )

        with pytest.raises(automatic_responses.cmd.get.AutomaticResponseNotFoundError):
            await lego_workflows.run_and_collect_events(
                automatic_responses.cmd.get.Command(
                    org_code=org_code,
                    automatic_response_id=created_automatic_response.automatic_response_id,
                    sql_conn=conn,
                )
            )
