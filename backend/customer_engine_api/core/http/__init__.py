"""Http module."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
import stamina

if TYPE_CHECKING:

    from customer_engine_api.core.typing import JsonResponse


@stamina.retry(on=httpx.HTTPStatusError, attempts=3)
def safe_return(response: httpx.Response) -> JsonResponse:
    """Safe return response."""
    response.raise_for_status()
    return response.json()
