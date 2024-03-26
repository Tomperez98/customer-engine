from __future__ import annotations

from uuid import UUID, uuid4

import lego_workflows
import pytest

from customer_engine_api import handlers
from customer_engine_api.core.config import resources


@pytest.mark.e2e()
async def test_list_unmatched_prompts() -> None:
    with resources.db_engine.begin() as conn:
        created_umatched_prompts: set[UUID] = set()
        for i in range(2):
            prompt_used = f"Unmatched prompt {i}"

            created, _ = await lego_workflows.run_and_collect_events(
                handlers.unmatched_prompts.register.Command(
                    org_code="test",
                    prompt=prompt_used,
                    sql_conn=conn,
                )
            )

            created_umatched_prompts.add(created.prompt_id)

        listed_umatched_promts, _ = await lego_workflows.run_and_collect_events(
            cmd=handlers.unmatched_prompts.list_all.Command(
                org_code="test", sql_conn=conn
            )
        )

        ids_for_listed: set[UUID] = {
            unmatched_prompt.prompt_id
            for unmatched_prompt in listed_umatched_promts.unmatched_prompts
        }

        assert created_umatched_prompts.issubset(ids_for_listed)

        for prompt_id in created_umatched_prompts:
            await lego_workflows.run_and_collect_events(
                cmd=handlers.unmatched_prompts.delete.Command(
                    org_code="test", prompt_id=prompt_id, sql_conn=conn
                )
            )


@pytest.mark.e2e()
async def test_get_not_existing() -> None:
    with (
        resources.db_engine.begin() as conn,
        pytest.raises(handlers.unmatched_prompts.get.UnmatchedResponseNotFoundError),
    ):
        await lego_workflows.run_and_collect_events(
            cmd=handlers.unmatched_prompts.get.Command(
                org_code="test", prompt_id=uuid4(), sql_conn=conn
            )
        )


@pytest.mark.e2e()
async def test_get_existing() -> None:
    with resources.db_engine.begin() as conn:
        created, _ = await lego_workflows.run_and_collect_events(
            handlers.unmatched_prompts.register.Command(
                org_code="test",
                prompt="Soy un unmatched prompt.",
                sql_conn=conn,
            )
        )
        existing, _ = await lego_workflows.run_and_collect_events(
            cmd=handlers.unmatched_prompts.get.Command(
                org_code="test", prompt_id=created.prompt_id, sql_conn=conn
            )
        )
        assert existing.unmatched_prompt.prompt_id == created.prompt_id
        assert existing.unmatched_prompt.org_code == "test"
        assert existing.unmatched_prompt.prompt == "Soy un unmatched prompt."

        deleted, _ = await lego_workflows.run_and_collect_events(
            cmd=handlers.unmatched_prompts.delete.Command(
                org_code="test", prompt_id=created.prompt_id, sql_conn=conn
            )
        )
        with pytest.raises(
            handlers.unmatched_prompts.get.UnmatchedResponseNotFoundError
        ):
            await lego_workflows.run_and_collect_events(
                cmd=handlers.unmatched_prompts.get.Command(
                    org_code="test", prompt_id=deleted.prompt_id, sql_conn=conn
                )
            )
