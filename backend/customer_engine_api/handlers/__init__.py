"""Application handlers."""

from __future__ import annotations

from customer_engine_api.handlers import (
    auth,
    automatic_responses,
    org_settings,
    whatsapp,
)

__all__ = ["auth", "automatic_responses", "org_settings", "whatsapp"]
