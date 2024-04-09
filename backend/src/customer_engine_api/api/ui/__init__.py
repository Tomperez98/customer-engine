"""Internal API."""

from __future__ import annotations

from fastapi import APIRouter

from customer_engine_api.api.ui import (
    automatic_responses,
    org_settings,
    unmatched_prompts,
    whatsapp_tokens,
)

router = APIRouter(prefix="/ui", tags=["ui"])


router.include_router(automatic_responses.router)
router.include_router(whatsapp_tokens.router)
router.include_router(org_settings.router)
router.include_router(unmatched_prompts.router)
