"""Health router."""
from __future__ import annotations

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/health", tags=["health"])


class HealthCheckResponse(BaseModel):
    """Health check response."""

    status: Literal["healthy", "not-healthy"]


@router.get(path="/health")
async def check() -> HealthCheckResponse:
    """Check application is ready."""
    return HealthCheckResponse(status="healthy")
