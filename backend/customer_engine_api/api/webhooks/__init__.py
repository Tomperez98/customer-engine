"""Webhook routes."""

from __future__ import annotations

import lego_workflows
from fastapi import APIRouter, Request, Response, status
from fastapi.exceptions import HTTPException

from customer_engine_api.config import resources
from customer_engine_api.logging import logger

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.get("/whatsapp/{org_code}")
async def suscribe_whatsapp_webhooks(org_code: str, req: Request) -> Response:  # noqa: D103
    from customer_engine_api.core import whatsapp
    from customer_engine_api.core.whatsapp import core

    verify_token = req.query_params["hub.verify_token"]
    with resources.db_engine.begin() as conn:
        response, events = await lego_workflows.run_and_collect_events(
            cmd=whatsapp.cmd.get_tokens.Command(org_code=org_code, sql_conn=conn)
        )
    await lego_workflows.publish_events(events=events)
    stored_tokens = response.whatsapp_token
    if not core.check_same_hashed(
        hashed=stored_tokens.user_token, string=verify_token, algo="sha256"
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return Response(content=req.query_params["hub.challenge"])


@router.post("/whatsapp/{org_code}")
async def whatsapp_webhooks(org_code: str, req: Request) -> None:  # noqa: ARG001, D103
    logger.debug(await req.json())
    raise NotImplementedError
