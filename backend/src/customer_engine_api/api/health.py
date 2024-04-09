"""Health router."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import text

from customer_engine_api.core.config import resources

router = APIRouter(prefix="/health", tags=["health"])


class HealthCheckResponse(BaseModel):
    """Health check response."""

    status: Literal["healthy"]


@router.get(path="/check")
async def check() -> HealthCheckResponse:
    """Check application is ready."""
    with resources.db_engine.begin() as conn:
        conn.execute(text("SELECT 1")).fetchone()
    return HealthCheckResponse(status="healthy")
