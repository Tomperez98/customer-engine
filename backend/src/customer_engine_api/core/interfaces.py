"""Interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Self

if TYPE_CHECKING:
    from sqlalchemy import Row


@dataclass(frozen=True)
class SqlQueriable(ABC):
    """Classes that implement this trait will be SQL queriable."""

    @classmethod
    @abstractmethod
    def from_row(cls: type[Self], row: Row[Any]) -> Self:
        """Instantiate class from SqlAlchemy row."""
        raise NotImplementedError
