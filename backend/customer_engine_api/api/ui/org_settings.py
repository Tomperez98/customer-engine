"""Org settings."""

from __future__ import annotations

from typing import Literal

import lego_workflows
from fastapi import APIRouter
from pydantic import BaseModel

from customer_engine_api import handlers
from customer_engine_api.api.ui.deps import BearerToken  # noqa: TCH001
from customer_engine_api.core import jwt, time
from customer_engine_api.core.config import resources
from customer_engine_api.core.org_settings import OrgSettings

router = APIRouter(prefix="/org-settings", tags=["org-settings"])


class ResponseGetOrgSettings(BaseModel):
    settings: OrgSettings


@router.get("")
async def get_org_settings(auth_token: BearerToken) -> ResponseGetOrgSettings:
    """Get org settings."""
    with resources.db_engine.begin() as conn:
        get_response, get_events = await lego_workflows.run_and_collect_events(
            handlers.org_settings.get_or_default.Command(
                org_code=jwt.decode_token(
                    encoded_token=auth_token.credentials, current_time=time.now()
                ).org_code,
                sql_conn=conn,
            )
        )
    await lego_workflows.publish_events(events=get_events)
    return ResponseGetOrgSettings(settings=get_response.settings)


class ResponseDeleteOrgSettings(BaseModel):
    status: Literal["deleted"]


@router.delete("")
async def delete_org_settings(auth_token: BearerToken) -> ResponseDeleteOrgSettings:
    with resources.db_engine.begin() as conn:
        _, delete_events = await lego_workflows.run_and_collect_events(
            handlers.org_settings.delete.Command(
                org_code=jwt.decode_token(
                    encoded_token=auth_token.credentials, current_time=time.now()
                ).org_code,
                sql_conn=conn,
            )
        )
    await lego_workflows.publish_events(events=delete_events)
    return ResponseDeleteOrgSettings(status="deleted")


class UpsertOrgSettings(BaseModel):
    default_response: str | None


class ResponseUpsertOrgSettings(BaseModel):
    settings: OrgSettings


@router.put("")
async def upsert_org_settings(
    auth_token: BearerToken,
    req: UpsertOrgSettings,
) -> ResponseUpsertOrgSettings:
    with resources.db_engine.begin() as conn:
        upsert_response, upsert_events = await lego_workflows.run_and_collect_events(
            handlers.org_settings.upsert.Command(
                org_code=jwt.decode_token(
                    encoded_token=auth_token.credentials, current_time=time.now()
                ).org_code,
                sql_conn=conn,
                default_response=req.default_response,
            )
        )
    await lego_workflows.publish_events(events=upsert_events)
    return ResponseUpsertOrgSettings(settings=upsert_response.settings)
