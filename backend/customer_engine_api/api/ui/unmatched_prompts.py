"""Unmatched prompts."""

from __future__ import annotations

from uuid import UUID

import lego_workflows
from fastapi import APIRouter, HTTPException, status
from lego_workflows.components import DomainError
from pydantic import BaseModel

from customer_engine_api import handlers
from customer_engine_api.api.ui.deps import BearerToken  # noqa: TCH001
from customer_engine_api.core import jwt, time
from customer_engine_api.core.config import resources
from customer_engine_api.core.unmatched_prompts import UnmatchedPrompt

router = APIRouter(prefix="/unmatched-prompts", tags=["unmatched-prompts"])


class ResponseListUnmatchedPrompts(BaseModel):  # noqa: D101
    unmatched_prompts: list[UnmatchedPrompt]


@router.get("")
async def list_unmatched_prompts(
    auth_token: BearerToken,
) -> ResponseListUnmatchedPrompts:
    """List unmatched prompts."""
    try:
        with resources.db_engine.begin() as conn:
            (
                listed_unmatched_prompts,
                events,
            ) = await lego_workflows.run_and_collect_events(
                cmd=handlers.unmatched_prompts.list_all.Command(
                    org_code=jwt.decode_token(
                        auth_token.credentials,
                        current_time=time.now(),
                    ).org_code,
                    sql_conn=conn,
                )
            )
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from None

    await lego_workflows.publish_events(events=events)

    return ResponseListUnmatchedPrompts(
        unmatched_prompts=listed_unmatched_prompts.unmatched_prompts
    )


class ResponseDeleteUnmatchedPrompt(BaseModel):  # noqa: D101
    deleted_unmatched_prompt: UUID


@router.delete("/{prompt_id}")
async def delete_unmatched_prompt(
    auth_token: BearerToken,
    prompt_id: UUID,
) -> ResponseDeleteUnmatchedPrompt:
    """Delete unmatched prompt."""
    try:
        with resources.db_engine.begin() as conn:
            deleted, events = await lego_workflows.run_and_collect_events(
                cmd=handlers.unmatched_prompts.delete.Command(
                    org_code=jwt.decode_token(
                        auth_token.credentials,
                        current_time=time.now(),
                    ).org_code,
                    prompt_id=prompt_id,
                    sql_conn=conn,
                )
            )
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from None

    await lego_workflows.publish_events(events=events)
    return ResponseDeleteUnmatchedPrompt(deleted_unmatched_prompt=deleted.prompt_id)
