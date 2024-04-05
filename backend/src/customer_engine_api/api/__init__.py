"""API routes."""

from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.middleware import Middleware
from fastapi.responses import ORJSONResponse
from lego_workflows.components import DomainError
from starlette.middleware.cors import CORSMiddleware

from customer_engine_api import handlers
from customer_engine_api.api import health, ui, webhooks

app = FastAPI(
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_origins=[
                "http://localhost:3000",
                "https://customer-engine.vercel.app",
            ],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ]
)


@app.exception_handler(DomainError)
async def handle_domain_error(req: Request, exc: DomainError) -> ORJSONResponse:
    """Handle domain error."""
    _ = req

    if isinstance(exc, handlers.whatsapp.get_tokens.WhatsappTokenNotFoundError):
        status_code = status.HTTP_404_NOT_FOUND
    else:
        status_code = status.HTTP_400_BAD_REQUEST
    return ORJSONResponse(content={"error": str(exc)}, status_code=status_code)


app.include_router(router=health.router)
app.include_router(router=ui.router)
app.include_router(router=webhooks.router)
