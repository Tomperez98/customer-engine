"""API routes."""

from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from lego_workflows.components import DomainError
from pydantic import BaseModel

from customer_engine_api.api import health, ui, webhooks

app = FastAPI(
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:3000"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=["*"],
        )
    ]
)
app.include_router(router=health.router)
app.include_router(router=ui.router)
app.include_router(router=webhooks.router)


class DomainErrorResponse(BaseModel):
    """Response model for domain error."""

    error: str


@app.exception_handler(DomainError)
async def handle_domain_errors(req: Request, exc: DomainError) -> ORJSONResponse:  # noqa: ARG001
    """Domain error handler."""
    return ORJSONResponse(
        content={
            "error": str(exc),
        },
        status_code=status.HTTP_400_BAD_REQUEST,
    )
