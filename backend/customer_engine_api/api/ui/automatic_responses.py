"""Automatic responses."""

from __future__ import annotations

from uuid import UUID

import lego_workflows
from fastapi import APIRouter
from pydantic import BaseModel

from customer_engine_api.config import resources
from customer_engine_api.core import automatic_responses
from customer_engine_api.core.automatic_responses.core import AutomaticResponse

router = APIRouter(prefix="/automatic-responses", tags=["automatic-responses"])


class CreateAutomaticResponse(BaseModel):  # noqa: D101
    name: str
    examples: list[str]
    response: str


class ResponseCreateAutomaticResponse(BaseModel):  # noqa: D101
    automatic_response_id: UUID


@router.post("")
async def create_automatic_response(
    req: CreateAutomaticResponse,
) -> ResponseCreateAutomaticResponse:
    """Create a new automatic response."""
    with resources.db_engine.begin() as conn:
        created_response, events = await lego_workflows.run_and_collect_events(
            cmd=automatic_responses.cmd.create.Command(
                org_code=resources.default_org,
                name=req.name,
                examples=req.examples,
                response=req.response,
                sql_conn=conn,
                qdrant_client=resources.clients.qdrant,
                cohere_client=resources.clients.cohere,
            )
        )

    await lego_workflows.publish_events(events=events)
    return ResponseCreateAutomaticResponse(
        automatic_response_id=created_response.automatic_response_id
    )


class ResponseGetAutomaticResponse(BaseModel):  # noqa: D101
    automatic_response: AutomaticResponse


@router.get("/{automatic_response_id}")
async def get_automatic_response(
    automatic_response_id: UUID,
) -> ResponseGetAutomaticResponse:
    """Get automatic response."""
    with resources.db_engine.begin() as conn:
        (
            existing_automatic_response,
            events,
        ) = await lego_workflows.run_and_collect_events(
            cmd=automatic_responses.cmd.get.Command(
                org_code=resources.default_org,
                automatic_response_id=automatic_response_id,
                sql_conn=conn,
            )
        )

    await lego_workflows.publish_events(events=events)

    return ResponseGetAutomaticResponse(
        automatic_response=existing_automatic_response.automatic_response
    )


class PatchAutomaticResponse(BaseModel):  # noqa: D101
    name: str | None
    examples: list[str] | None
    response: str | None


class ResponsePatchAutomaticResponse(BaseModel):  # noqa: D101
    updated_automatic_response: AutomaticResponse


@router.patch("/{automatic_response_id}")
async def patch_automatic_response(  # noqa: D103
    automatic_response_id: UUID,
    req: PatchAutomaticResponse,
) -> ResponsePatchAutomaticResponse:
    with resources.db_engine.begin() as conn:
        updated_response, events = await lego_workflows.run_and_collect_events(
            cmd=automatic_responses.cmd.update.Command(
                org_code=resources.default_org,
                automatic_response_id=automatic_response_id,
                new_name=req.name,
                new_examples=req.examples,
                new_response=req.response,
                sql_conn=conn,
                cohere_client=resources.clients.cohere,
                qdrant_client=resources.clients.qdrant,
            )
        )

    await lego_workflows.publish_events(events=events)
    return ResponsePatchAutomaticResponse(
        updated_automatic_response=updated_response.updated_automatic_response
    )


class ResponseListAutomaticResponse(BaseModel):  # noqa: D101
    automatic_response: list[AutomaticResponse]


@router.get("")
async def list_automatic_responses() -> ResponseListAutomaticResponse:  # noqa: D103
    with resources.db_engine.begin() as conn:
        (
            listed_automatic_responses,
            events,
        ) = await lego_workflows.run_and_collect_events(
            cmd=automatic_responses.cmd.list.Command(
                org_code=resources.default_org, sql_conn=conn
            )
        )

    await lego_workflows.publish_events(events=events)
    return ResponseListAutomaticResponse(
        automatic_response=listed_automatic_responses.automatic_responses
    )


class ResponseDeleteAutomaticResponse(BaseModel):  # noqa: D101
    automatic_response_id: UUID


@router.delete("/{automatic_response_id}")
async def delete_automatic_response(  # noqa: D103
    automatic_response_id: UUID,
) -> ResponseDeleteAutomaticResponse:
    with resources.db_engine.begin() as conn:
        deleted_response, events = await lego_workflows.run_and_collect_events(
            cmd=automatic_responses.cmd.delete.Command(
                org_code=resources.default_org,
                automatic_response_id=automatic_response_id,
                sql_conn=conn,
                qdrant_client=resources.clients.qdrant,
            )
        )

    await lego_workflows.publish_events(events=events)
    return ResponseDeleteAutomaticResponse(
        automatic_response_id=deleted_response.automatic_response_id
    )


class ResponseSearchByPromptAutomaticResponse(BaseModel):  # noqa: D101
    automatic_response: AutomaticResponse | None


@router.get("/search/by-prompt")
async def search_by_prompt(prompt: str) -> ResponseSearchByPromptAutomaticResponse:  # noqa: D103
    with resources.db_engine.begin() as conn:
        (
            result_automatic_response,
            events,
        ) = await lego_workflows.run_and_collect_events(
            automatic_responses.cmd.search_by_prompt.Command(
                org_code=resources.default_org,
                prompt=prompt,
                sql_conn=conn,
                cohere_client=resources.clients.cohere,
                qdrant_client=resources.clients.qdrant,
            )
        )

    await lego_workflows.publish_events(events=events)

    return ResponseSearchByPromptAutomaticResponse(
        automatic_response=result_automatic_response.automatic_response
    )
