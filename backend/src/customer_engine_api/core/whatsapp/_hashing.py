"""Hashing."""

from __future__ import annotations

import hashlib
from typing import Literal, TypeAlias, assert_never

HashAlgorithms: TypeAlias = Literal["sha256"]


def hash_string(string: str, algo: HashAlgorithms) -> str:
    """Hash string."""
    if algo == "sha256":
        return hashlib.sha256(string.encode()).hexdigest()

    assert_never(algo)


def check_same_hashed(hashed: str, string: str, algo: HashAlgorithms) -> bool:
    """Check if user token is equal to class user token."""
    return hashed == hash_string(string=string, algo=algo)
