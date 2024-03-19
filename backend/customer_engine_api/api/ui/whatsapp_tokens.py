"""Whatsapp tokens."""

from __future__ import annotations

from typing import Literal

import lego_workflows
from fastapi import APIRouter, HTTPException, status
from lego_workflows.components import DomainError
from pydantic import BaseModel

from customer_engine_api import handlers
from customer_engine_api.api.ui._deps import BearerToken  # noqa: TCH001
from customer_engine_api.core import jwt, time
from customer_engine_api.core.config import resources
from customer_engine_api.core.whatsapp import WhatsappTokens

router = APIRouter(prefix="/whatsapp-tokens", tags=["whatsapp-tokens"])


class ResponseGetWhatsappTokens(BaseModel):  # noqa: D101
    token: WhatsappTokens


@router.get("")
async def get_whatsapp_tokens(
    auth_token: BearerToken,
) -> ResponseGetWhatsappTokens:
    """Get whatsapp tokens."""
    try:
        with resources.db_engine.begin() as conn:
            whatsapp_token, events = await lego_workflows.run_and_collect_events(
                cmd=handlers.whatsapp.get_tokens.Command(
                    org_code=jwt.decode_token(
                        auth_token.credentials,
                        current_time=time.now(),
                    ).org_code,
                    sql_conn=conn,
                )
            )
    except handlers.whatsapp.get_tokens.WhatsappTokenNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from None
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from None

    await lego_workflows.publish_events(events=events)
    return ResponseGetWhatsappTokens(token=whatsapp_token.whatsapp_token)


class CreateWhatsappTokens(BaseModel):  # noqa: D101
    access_token: str
    user_token: str


class ResponseCreateWhatsappTokens(BaseModel):  # noqa: D101
    status: Literal["created"]


@router.post("")
async def create_whatsapp_tokens(
    auth_token: BearerToken,
    req: CreateWhatsappTokens,
) -> ResponseCreateWhatsappTokens:
    """Create a whatsapp token."""
    try:
        with resources.db_engine.begin() as conn:
            _, events = await lego_workflows.run_and_collect_events(
                cmd=handlers.whatsapp.register_tokens.Command(
                    org_code=jwt.decode_token(
                        auth_token.credentials,
                        current_time=time.now(),
                    ).org_code,
                    sql_conn=conn,
                    access_token=req.access_token,
                    user_token=req.user_token,
                )
            )
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from None
    await lego_workflows.publish_events(events=events)
    return ResponseCreateWhatsappTokens(status="created")


class ResponseDeleteWhatsappTokens(BaseModel):  # noqa: D101
    status: Literal["deleted"]


@router.delete("")
async def delete_whatsapp_tokens(  # noqa: D103
    auth_token: BearerToken,
) -> ResponseDeleteWhatsappTokens:
    try:
        with resources.db_engine.begin() as conn:
            _, events = await lego_workflows.run_and_collect_events(
                cmd=handlers.whatsapp.delete_tokens.Command(
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
    return ResponseDeleteWhatsappTokens(status="deleted")


class PatchWhatsappTokens(BaseModel):  # noqa: D101
    access_token: str | None
    user_token: str | None


class ResponsePatchWhatsappTokens(BaseModel):  # noqa: D101
    status: Literal["updated"]


@router.patch("")
async def patch_whatsapp_tokens(
    auth_token: BearerToken,
    req: PatchWhatsappTokens,
) -> ResponsePatchWhatsappTokens:
    """Patch whatsapp token."""
    try:
        with resources.db_engine.begin() as conn:
            _, events = await lego_workflows.run_and_collect_events(
                cmd=handlers.whatsapp.update_tokens.Command(
                    org_code=jwt.decode_token(
                        auth_token.credentials,
                        current_time=time.now(),
                    ).org_code,
                    new_access_token=req.access_token,
                    new_user_token=req.user_token,
                    sql_conn=conn,
                )
            )
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from None

    await lego_workflows.publish_events(events=events)
    return ResponsePatchWhatsappTokens(status="updated")
