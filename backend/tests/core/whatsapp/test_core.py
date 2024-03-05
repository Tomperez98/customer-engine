from __future__ import annotations

import hashlib

import pytest

from customer_engine_api.core.whatsapp import core


@pytest.mark.unit()
def test_check_hash() -> None:
    assert core.check_same_hashed(
        hashed=hashlib.sha256(b"HELLO").hexdigest(), string="HELLO", algo="sha256"
    )
