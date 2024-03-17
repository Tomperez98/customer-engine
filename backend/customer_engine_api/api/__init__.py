"""API routes."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from customer_engine_api.api import health, ui, webhooks

app = FastAPI(
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:3000"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ]
)
app.include_router(router=health.router)
app.include_router(router=ui.router)
app.include_router(router=webhooks.router)
