"""Typing module."""

from __future__ import annotations

from typing import Any, Literal, TypeAlias

Environment: TypeAlias = Literal["staging", "development"]
Json: TypeAlias = dict[str, Any]
JsonResponse: TypeAlias = Json | list[Json]
