"""Unmatched prompts."""

from __future__ import annotations

from typing import Literal
from uuid import UUID

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


class AddToAutomaticResponseAsExample(BaseModel):
    prompt_ids: list[UUID]
    automatic_response_id: UUID


class ResponseAddToAutomaticResponseAsExample(BaseModel):
    example_ids: list[UUID]


@router.post(path="/add-to-automatic-response-as-examples")
async def add_to_automatic_response_as_example(
    req: AddToAutomaticResponseAsExample,
    auth_token: BearerToken,
) -> ResponseAddToAutomaticResponseAsExample:
    auth_response = await process_token(token=auth_token, current_time=now())
    with resources.db_engine.begin() as conn:
        response, events = await lego_workflows.run_and_collect_events(
            handlers.unmatched_prompts.bulk_add_to_auto_res_as_example.Command(
                org_code=auth_response.org_code,
                prompt_ids=req.prompt_ids,
                automatic_response_id=req.automatic_response_id,
                sql_conn=conn,
                qdrant_client=resources.clients.qdrant,
                cohere_client=resources.clients.cohere,
            )
        )

    await lego_workflows.publish_events(events=events)
    return ResponseAddToAutomaticResponseAsExample(example_ids=response.example_ids)


class ResponseDeleteUnmatchedPrompt(BaseModel):
    status: Literal["deleted"]


@router.delete(path="/{unmatched_prompt_id}")
async def delete_unmatched_prompt(
    unmatched_prompt_id: UUID,
    auth_token: BearerToken,
) -> ResponseDeleteUnmatchedPrompt:
    auth_response = await process_token(token=auth_token, current_time=now())
    with resources.db_engine.begin() as conn:
        _, events = await lego_workflows.run_and_collect_events(
            handlers.unmatched_prompts.delete_unmatched_prompt.Command(
                org_code=auth_response.org_code,
                prompt_id=unmatched_prompt_id,
                sql_conn=conn,
            )
        )

    await lego_workflows.publish_events(events=events)
    return ResponseDeleteUnmatchedPrompt(status="deleted")


class ResponseDeleteAllUnmatchedPrompts(BaseModel):
    status: Literal["deleted"]


@router.delete(path="")
async def delete_all_unmatched_prompt(
    auth_token: BearerToken,
) -> ResponseDeleteAllUnmatchedPrompts:
    auth_response = await process_token(token=auth_token, current_time=now())
    with resources.db_engine.begin() as conn:
        _, events = await lego_workflows.run_and_collect_events(
            handlers.unmatched_prompts.delete_all.Command(
                org_code=auth_response.org_code,
                sql_conn=conn,
            )
        )

    await lego_workflows.publish_events(events=events)
    return ResponseDeleteAllUnmatchedPrompts(status="deleted")
