"""Internal API."""
from __future__ import annotations

from fastapi import APIRouter

from customer_engine.api.ui import forms

router = APIRouter(prefix="/ui", tags=["ui"])
router.include_router(forms.router)
