"""Unmatched prompts."""

from __future__ import annotations

import lego_workflows
from fastapi import APIRouter
from pydantic import BaseModel

from customer_engine_api import handlers
from customer_engine_api.api.ui.deps import BearerToken  # noqa: TCH001
from customer_engine_api.api.ui.utils import process_token
from customer_engine_api.core.automatic_responses import UnmatchedPrompt
from customer_engine_api.core.config import resources
from customer_engine_api.core.time import now

router = APIRouter(prefix="/unmatched-prompts", tags=["unmatched-prompts"])


class ResponseListUnmatchedPrompts(BaseModel):
    unmatched_prompts: list[UnmatchedPrompt]


@router.get(path="")
async def list_unmatched_prompts(
    auth_token: BearerToken,
) -> ResponseListUnmatchedPrompts:
    auth_response = await process_token(token=auth_token, current_time=now())
    with resources.db_engine.begin() as conn:
        response, events = await lego_workflows.run_and_collect_events(
            handlers.unmatched_prompts.list_unmatched_prompts.Command(
                org_code=auth_response.org_code, sql_conn=conn
            )
        )

    await lego_workflows.publish_events(events=events)
    return ResponseListUnmatchedPrompts(unmatched_prompts=response.unmatched_prompts)
