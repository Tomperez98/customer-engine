"""Utility functions UI API."""

from __future__ import annotations

from typing import TYPE_CHECKING

import lego_workflows

from customer_engine_api import handlers

if TYPE_CHECKING:
    import datetime

    from fastapi.security import HTTPAuthorizationCredentials


async def process_token(
    token: HTTPAuthorizationCredentials, current_time: datetime.datetime
) -> handlers.auth.validate_token.Response:
    """Process token."""
    response, events = await lego_workflows.run_and_collect_events(
        cmd=handlers.auth.validate_token.Command(token=token, current_time=current_time)
    )

    await lego_workflows.publish_events(events=events)

    return response
