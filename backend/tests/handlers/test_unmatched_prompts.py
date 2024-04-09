from __future__ import annotations

from uuid import uuid4

import lego_workflows
import pytest

from customer_engine_api import handlers
from customer_engine_api.core.config import resources
from customer_engine_api.core.time import now


@pytest.mark.e2e()
async def test_retrieve_unmatched_prompt() -> None:
    org_code = "test"
    current_time = now()
    with (
        resources.db_engine.begin() as conn,
    ):
        response_register, _ = await lego_workflows.run_and_collect_events(
            handlers.unmatched_prompts.register_unmatched_prompt.Command(
                org_code=org_code,
                prompt="I'm an unmatched prompt",
                current_time=current_time,
                sql_conn=conn,
            )
        )
        response_get, _ = await lego_workflows.run_and_collect_events(
            cmd=handlers.unmatched_prompts.get_unmatched_prompt.Command(
                org_code=org_code,
                prompt_id=response_register.umatched_prompt_id,
                sql_conn=conn,
            )
        )

        assert response_get.unmatched_prompt.created_at == current_time.replace(
            tzinfo=None
        )
        assert response_get.unmatched_prompt.prompt == "I'm an unmatched prompt"

        response_list, _ = await lego_workflows.run_and_collect_events(
            handlers.unmatched_prompts.list_unmatched_prompts.Command(
                org_code=org_code, sql_conn=conn
            )
        )
        assert len(response_list.unmatched_prompts) == 1
        assert (
            response_list.unmatched_prompts[0].prompt_id
            == response_register.umatched_prompt_id
        )

        await lego_workflows.run_and_collect_events(
            cmd=handlers.unmatched_prompts.delete_unmatched_prompt.Command(
                org_code=org_code,
                prompt_id=response_register.umatched_prompt_id,
                sql_conn=conn,
            )
        )

        with pytest.raises(
            handlers.unmatched_prompts.get_unmatched_prompt.UnmatchedPromptNotFoundError
        ):
            await lego_workflows.run_and_collect_events(
                cmd=handlers.unmatched_prompts.get_unmatched_prompt.Command(
                    org_code=org_code,
                    prompt_id=response_register.umatched_prompt_id,
                    sql_conn=conn,
                )
            )


@pytest.mark.e2e()
async def test_not_existing_unmatched_prompt() -> None:
    with (
        resources.db_engine.begin() as conn,
        pytest.raises(
            handlers.unmatched_prompts.get_unmatched_prompt.UnmatchedPromptNotFoundError
        ),
    ):
        await lego_workflows.run_and_collect_events(
            cmd=handlers.unmatched_prompts.get_unmatched_prompt.Command(
                org_code="test", prompt_id=uuid4(), sql_conn=conn
            )
        )
