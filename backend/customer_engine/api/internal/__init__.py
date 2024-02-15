"""Internal API."""
from __future__ import annotations

from fastapi import APIRouter

from customer_engine.api.internal import forms

router = APIRouter(prefix="/internal", tags=["internal"])
router.include_router(forms.router)
