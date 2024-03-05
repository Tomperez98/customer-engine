"""Whatsapp tokens."""

from __future__ import annotations

from typing import Literal

import lego_workflows
from fastapi import APIRouter
from pydantic import BaseModel

from customer_engine_api.config import resources
from customer_engine_api.core import whatsapp
from customer_engine_api.core.whatsapp.core import WhatsappTokens

router = APIRouter(prefix="/whatsapp-tokens", tags=["whatsapp-tokens"])


class ResponseGetWhatsappTokens(BaseModel):  # noqa: D101
    token: WhatsappTokens


@router.get("")
async def get_whatsapp_tokens() -> ResponseGetWhatsappTokens:
    """Get whatsapp tokens."""
    with resources.db_engine.begin() as conn:
        whatsapp_token, events = await lego_workflows.run_and_collect_events(
            cmd=whatsapp.cmd.get_tokens.Command(
                org_code=resources.default_org, sql_conn=conn
            )
        )

    await lego_workflows.publish_events(events=events)
    return ResponseGetWhatsappTokens(token=whatsapp_token.whatsapp_token)


class CreateWhatsappTokens(BaseModel):  # noqa: D101
    access_token: str
    user_token: str


class ResponseCreateWhatsappTokens(BaseModel):  # noqa: D101
    status: Literal["created"]


@router.post("")
async def create_whatsapp_tokens(
    req: CreateWhatsappTokens,
) -> ResponseCreateWhatsappTokens:
    """Create a whatsapp token."""
    with resources.db_engine.begin() as conn:
        _, events = await lego_workflows.run_and_collect_events(
            cmd=whatsapp.cmd.register_tokens.Command(
                org_code=resources.default_org,
                sql_conn=conn,
                access_token=req.access_token,
                user_token=req.user_token,
            )
        )
    await lego_workflows.publish_events(events=events)
    return ResponseCreateWhatsappTokens(status="created")


class ResponseDeleteWhatsappTokens(BaseModel):  # noqa: D101
    status: Literal["deleted"]


@router.delete("")
async def delete_whatsapp_tokens() -> ResponseDeleteWhatsappTokens:  # noqa: D103
    with resources.db_engine.begin() as conn:
        _, events = await lego_workflows.run_and_collect_events(
            cmd=whatsapp.cmd.delete_tokens.Command(
                org_code=resources.default_org,
                sql_conn=conn,
            )
        )
    await lego_workflows.publish_events(events=events)
    return ResponseDeleteWhatsappTokens(status="deleted")


class PatchWhatsappTokens(BaseModel):  # noqa: D101
    new_access_token: str | None
    new_user_token: str | None


class ResponsePatchWhatsappTokens(BaseModel):  # noqa: D101
    status: Literal["updated"]


@router.patch("")
async def patch_whatsapp_tokens(  # noqa: D103
    req: PatchWhatsappTokens,
) -> ResponsePatchWhatsappTokens:
    with resources.db_engine.begin() as conn:
        _, events = await lego_workflows.run_and_collect_events(
            cmd=whatsapp.cmd.update_tokens.Command(
                org_code=resources.default_org,
                new_access_token=req.new_access_token,
                new_user_token=req.new_user_token,
                sql_conn=conn,
            )
        )

    await lego_workflows.publish_events(events=events)
    return ResponsePatchWhatsappTokens(status="updated")
