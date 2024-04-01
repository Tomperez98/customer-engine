"""Webhook routes."""

from __future__ import annotations

from typing import TYPE_CHECKING

import lego_workflows
from fastapi import APIRouter, Request, Response, status
from fastapi.exceptions import HTTPException
from lego_workflows.components import DomainError

from customer_engine_api import handlers
from customer_engine_api.core import whatsapp
from customer_engine_api.core.config import resources

if TYPE_CHECKING:
    from customer_engine_api.core.typing import JsonResponse

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.get("/whatsapp/{org_code}")
async def suscribe_whatsapp_webhooks(org_code: str, req: Request) -> Response:  # noqa: D103
    verify_token = req.query_params["hub.verify_token"]
    with resources.db_engine.begin() as conn:
        response, events = await lego_workflows.run_and_collect_events(
            cmd=handlers.whatsapp.get_tokens.Command(org_code=org_code, sql_conn=conn)
        )
    await lego_workflows.publish_events(events=events)
    stored_tokens = response.whatsapp_token
    if not whatsapp.hashing.check_same_hashed(
        hashed=stored_tokens.user_token, string=verify_token, algo="sha256"
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return Response(content=req.query_params["hub.challenge"])


@router.post("/whatsapp/{org_code}")
async def whatsapp_webhooks(org_code: str, req: Request) -> Response:  # noqa: D103
    payload: JsonResponse = await req.json()
    try:
        with resources.db_engine.begin() as conn:
            await lego_workflows.run_and_collect_events(
                cmd=handlers.whatsapp.react_to_webhook_event.Command(
                    payload=payload,
                    org_code=org_code,
                    qdrant_client=resources.clients.qdrant,
                    cohere_client=resources.clients.cohere,
                    sql_conn=conn,
                )
            )
    except DomainError:
        return Response()

    return Response()
