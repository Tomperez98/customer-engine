"""API routes."""
from __future__ import annotations

from fastapi import APIRouter

from customer_engine.web.api import whatsapp

router = APIRouter(prefix="/api", tags=["api"])


router.include_router(router=whatsapp.router)
