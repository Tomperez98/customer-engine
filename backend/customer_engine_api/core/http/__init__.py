"""Http module."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import httpx

    from customer_engine_api.core.typing import JsonResponse


def safe_return(response: httpx.Response) -> JsonResponse:
    """Safe return response."""
    response.raise_for_status()
    return response.json()
