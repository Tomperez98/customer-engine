"""Automatic response constants."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from customer_engine.commands.automatic_responses.core.typing import EmbeddingModels

DEFAULT_EMBEDDING_MODEL: EmbeddingModels = "cohere:embed-multilingual-light-v3.0"
