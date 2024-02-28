"""Internal API."""
from __future__ import annotations

from fastapi import APIRouter

from backend.api.ui import automatic_responses, unmatched_prompts

router = APIRouter(prefix="/ui", tags=["ui"])


router.include_router(automatic_responses.router)
router.include_router(unmatched_prompts.router)
