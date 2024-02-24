"""Internal API."""
from __future__ import annotations

from fastapi import APIRouter

from customer_engine.api.ui import automatic_responses

router = APIRouter(prefix="/ui", tags=["ui"])
router.include_router(automatic_responses.router)
