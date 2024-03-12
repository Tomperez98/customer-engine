"""Hashing."""

from __future__ import annotations

import hashlib
from typing import Literal, TypeAlias, assert_never

HashAlgorithms: TypeAlias = Literal["sha256"]


def hash_string(string: str, algo: HashAlgorithms) -> str:
    """Hash string."""
    hashed_string: str
    if algo == "sha256":
        hashed_string = hashlib.sha256(string.encode()).hexdigest()
    else:
        assert_never(algo)
    return hashed_string


def check_same_hashed(hashed: str, string: str, algo: HashAlgorithms) -> bool:
    """Check if user token is equal to class user token."""
    return hashed == hash_string(string=string, algo=algo)
