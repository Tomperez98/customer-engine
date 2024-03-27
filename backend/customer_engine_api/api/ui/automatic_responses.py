"""Automatic responses."""

from __future__ import annotations

from typing import Literal
from uuid import UUID

import lego_workflows
from fastapi import APIRouter, HTTPException, status
from lego_workflows.components import DomainError
from pydantic import BaseModel

from customer_engine_api import handlers
from customer_engine_api.api.ui.deps import BearerToken  # noqa: TCH001
from customer_engine_api.core import jwt, time
from customer_engine_api.core.automatic_responses import AutomaticResponse, Example
from customer_engine_api.core.config import resources

router = APIRouter(prefix="/automatic-responses", tags=["automatic-responses"])


class UpdateExample(BaseModel):  # noqa: D101
    example: str | None


class ResponseUpdateExample(BaseModel):  # noqa: D101
    example: Example


@router.patch(path="/{automatic_response_id}/example/{example_id}")
async def update_example(
    auth_token: BearerToken,
    automatic_response_id: UUID,
    example_id: UUID,
    req: UpdateExample,
) -> ResponseUpdateExample:
    """Update example."""
    try:
        with resources.db_engine.begin() as conn:
            response, events = await lego_workflows.run_and_collect_events(
                cmd=handlers.automatic_responses.update_example.Command(
                    org_code=jwt.decode_token(
                        auth_token.credentials,
                        current_time=time.now(),
                    ).org_code,
                    automatic_response_id=automatic_response_id,
                    example_id=example_id,
                    sql_conn=conn,
                    cohere_client=resources.clients.cohere,
                    qdrant_client=resources.clients.qdrant,
                    example=req.example,
                )
            )
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from None

    await lego_workflows.publish_events(events=events)
    return ResponseUpdateExample(example=response.example)


class ResponseGetExample(BaseModel):  # noqa: D101
    example: Example


@router.get(path="/{automatic_response_id}/example/{example_id}")
async def get_example(
    auth_token: BearerToken, automatic_response_id: UUID, example_id: UUID
) -> ResponseGetExample:
    """Get example."""
    try:
        with resources.db_engine.begin() as conn:
            response, events = await lego_workflows.run_and_collect_events(
                cmd=handlers.automatic_responses.get_example.Command(
                    org_code=jwt.decode_token(
                        auth_token.credentials,
                        current_time=time.now(),
                    ).org_code,
                    automatic_response_id=automatic_response_id,
                    example_id=example_id,
                    sql_conn=conn,
                )
            )
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from None

    await lego_workflows.publish_events(events=events)
    return ResponseGetExample(example=response.example)


class ResponseDeleteExample(BaseModel):  # noqa: D101
    status: Literal["deleted"]


@router.delete(path="/{automatic_response_id}/example/{example_id}")
async def delete_example(
    auth_token: BearerToken, automatic_response_id: UUID, example_id: UUID
) -> ResponseDeleteExample:
    """Delete example."""
    try:
        with resources.db_engine.begin() as conn:
            _, events = await lego_workflows.run_and_collect_events(
                cmd=handlers.automatic_responses.delete_example.Command(
                    org_code=jwt.decode_token(
                        auth_token.credentials,
                        current_time=time.now(),
                    ).org_code,
                    automatic_response_id=automatic_response_id,
                    example_id=example_id,
                    sql_conn=conn,
                    qdrant_client=resources.clients.qdrant,
                )
            )
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from None

    await lego_workflows.publish_events(events=events)
    return ResponseDeleteExample(status="deleted")


class ResponseListExample(BaseModel):  # noqa: D101
    examples: list[Example]


@router.get(path="/{automatic_response_id}/example")
async def list_examples(
    auth_token: BearerToken, automatic_response_id: UUID
) -> ResponseListExample:
    """List examples."""
    try:
        with resources.db_engine.begin() as conn:
            response, events = await lego_workflows.run_and_collect_events(
                cmd=handlers.automatic_responses.list_examples.Command(
                    org_code=jwt.decode_token(
                        auth_token.credentials,
                        current_time=time.now(),
                    ).org_code,
                    automatic_response_id=automatic_response_id,
                    sql_conn=conn,
                )
            )
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from None

    await lego_workflows.publish_events(events=events)
    return ResponseListExample(examples=response.examples)


class CreateExample(BaseModel):  # noqa: D101
    example: str


class ResponseCreateExample(BaseModel):  # noqa: D101
    example_id: UUID


@router.post(path="/{automatic_response_id}/example")
async def create_example(
    auth_token: BearerToken, automatic_response_id: UUID, req: CreateExample
) -> ResponseCreateExample:
    """Create example."""
    try:
        with resources.db_engine.begin() as conn:
            response, events = await lego_workflows.run_and_collect_events(
                cmd=handlers.automatic_responses.create_example.Command(
                    org_code=jwt.decode_token(
                        auth_token.credentials,
                        current_time=time.now(),
                    ).org_code,
                    automatic_response_id=automatic_response_id,
                    example=req.example,
                    qdrant_client=resources.clients.qdrant,
                    cohere_client=resources.clients.cohere,
                    sql_conn=conn,
                )
            )
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from None

    await lego_workflows.publish_events(events=events)
    return ResponseCreateExample(example_id=response.example_id)


class CreateAutomaticResponse(BaseModel):  # noqa: D101
    name: str
    response: str


class ResponseCreateAutomaticResponse(BaseModel):  # noqa: D101
    automatic_response_id: UUID


@router.post("")
async def create_automatic_response(
    auth_token: BearerToken,
    req: CreateAutomaticResponse,
) -> ResponseCreateAutomaticResponse:
    """Create a new automatic response."""
    try:
        with resources.db_engine.begin() as conn:
            created_response, events = await lego_workflows.run_and_collect_events(
                cmd=handlers.automatic_responses.create_auto_resp.Command(
                    org_code=jwt.decode_token(
                        auth_token.credentials,
                        current_time=time.now(),
                    ).org_code,
                    name=req.name,
                    response=req.response,
                    sql_conn=conn,
                )
            )
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from None

    await lego_workflows.publish_events(events=events)
    return ResponseCreateAutomaticResponse(
        automatic_response_id=created_response.automatic_response_id
    )


class ResponseGetAutomaticResponse(BaseModel):  # noqa: D101
    automatic_response: AutomaticResponse


@router.get("/{automatic_response_id}")
async def get_automatic_response(
    automatic_response_id: UUID,
    auth_token: BearerToken,
) -> ResponseGetAutomaticResponse:
    """Get automatic response."""
    try:
        with resources.db_engine.begin() as conn:
            (
                existing_automatic_response,
                events,
            ) = await lego_workflows.run_and_collect_events(
                cmd=handlers.automatic_responses.get_auto_res.Command(
                    org_code=jwt.decode_token(
                        auth_token.credentials,
                        current_time=time.now(),
                    ).org_code,
                    automatic_response_id=automatic_response_id,
                    sql_conn=conn,
                )
            )
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from None

    await lego_workflows.publish_events(events=events)

    return ResponseGetAutomaticResponse(
        automatic_response=existing_automatic_response.automatic_response
    )


class PatchAutomaticResponse(BaseModel):  # noqa: D101
    name: str | None
    response: str | None


class ResponsePatchAutomaticResponse(BaseModel):  # noqa: D101
    updated_automatic_response: AutomaticResponse


@router.patch("/{automatic_response_id}")
async def patch_automatic_response(  # noqa: D103
    auth_token: BearerToken,
    automatic_response_id: UUID,
    req: PatchAutomaticResponse,
) -> ResponsePatchAutomaticResponse:
    try:
        with resources.db_engine.begin() as conn:
            updated_response, events = await lego_workflows.run_and_collect_events(
                cmd=handlers.automatic_responses.update_auto_res.Command(
                    org_code=jwt.decode_token(
                        auth_token.credentials,
                        current_time=time.now(),
                    ).org_code,
                    automatic_response_id=automatic_response_id,
                    new_name=req.name,
                    new_response=req.response,
                    sql_conn=conn,
                )
            )
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from None

    await lego_workflows.publish_events(events=events)
    return ResponsePatchAutomaticResponse(
        updated_automatic_response=updated_response.updated_automatic_response
    )


class ResponseListAutomaticResponse(BaseModel):  # noqa: D101
    automatic_response: list[AutomaticResponse]


@router.get("")
async def list_automatic_responses(  # noqa: D103
    auth_token: BearerToken,
) -> ResponseListAutomaticResponse:
    try:
        with resources.db_engine.begin() as conn:
            (
                listed_automatic_responses,
                events,
            ) = await lego_workflows.run_and_collect_events(
                cmd=handlers.automatic_responses.list_auto_res.Command(
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
    return ResponseListAutomaticResponse(
        automatic_response=listed_automatic_responses.automatic_responses
    )


class ResponseDeleteAutomaticResponse(BaseModel):  # noqa: D101
    status: Literal["deleted"]


@router.delete("/{automatic_response_id}")
async def delete_automatic_response(  # noqa: D103
    auth_token: BearerToken,
    automatic_response_id: UUID,
) -> ResponseDeleteAutomaticResponse:
    try:
        with resources.db_engine.begin() as conn:
            _, events = await lego_workflows.run_and_collect_events(
                cmd=handlers.automatic_responses.delete_auto_res.Command(
                    org_code=jwt.decode_token(
                        auth_token.credentials,
                        current_time=time.now(),
                    ).org_code,
                    automatic_response_id=automatic_response_id,
                    sql_conn=conn,
                    qdrant_client=resources.clients.qdrant,
                )
            )
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from None

    await lego_workflows.publish_events(events=events)
    return ResponseDeleteAutomaticResponse(status="deleted")


class SearchByPrompt(BaseModel):  # noqa: D101
    prompt: str


class ResponseSearchByPrompt(BaseModel):  # noqa: D101
    automatic_response: AutomaticResponse


@router.post("/search/by-prompt")
async def search_automatic_response_by_prompt(
    auth_token: BearerToken, req: SearchByPrompt
) -> ResponseSearchByPrompt:
    """Search automatic response by prompt."""
    try:
        with resources.db_engine.begin() as conn:
            response, events = await lego_workflows.run_and_collect_events(
                cmd=handlers.automatic_responses.get_auto_res_owns_example.Command(
                    org_code=jwt.decode_token(
                        auth_token.credentials,
                        current_time=time.now(),
                    ).org_code,
                    example_id_or_prompt=req.prompt,
                    sql_conn=conn,
                    qdrant_client=resources.clients.qdrant,
                    cohere_client=resources.clients.cohere,
                )
            )

    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from None

    await lego_workflows.publish_events(events=events)
    return ResponseSearchByPrompt(automatic_response=response.automatic_response)
