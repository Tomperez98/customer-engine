"""Time module."""

from __future__ import annotations

import datetime


def now() -> datetime.datetime:
    """Get current time in UTC."""
    return datetime.datetime.now(tz=datetime.UTC)
