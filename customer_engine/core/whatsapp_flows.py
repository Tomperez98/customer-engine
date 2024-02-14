"""Whatsapp Flows."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from mashumaro.mixins.orjson import DataClassORJSONMixin


@dataclass()
class WhatsAppFlow(DataClassORJSONMixin):
    """WhatsApp Flow."""

    flow_id: str
    name: str
    description: str
    metadata: dict[str, Any]
