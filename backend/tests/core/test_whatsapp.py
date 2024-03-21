from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING

import pytest

from customer_engine_api.core import whatsapp

if TYPE_CHECKING:
    from customer_engine_api.core.typing import JsonResponse


@pytest.mark.unit()
def test_check_hash() -> None:
    assert whatsapp.hashing.check_same_hashed(
        hashed=hashlib.sha256(b"HELLO").hexdigest(), string="HELLO", algo="sha256"
    )


@pytest.mark.unit()
@pytest.mark.parametrize(
    argnames=["payload", "expected"],
    argvalues=[
        (
            {
                "object": "whatsapp_business_account",
                "entry": [
                    {
                        "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
                        "changes": [
                            {
                                "value": {
                                    "messaging_product": "whatsapp",
                                    "metadata": {
                                        "display_phone_number": "PHONE_NUMBER",
                                        "phone_number_id": "123",
                                    },
                                    "contacts": [
                                        {
                                            "profile": {"name": "NAME"},
                                            "wa_id": "PHONE_NUMBER",
                                        }
                                    ],
                                    "messages": [
                                        {
                                            "from": "PHONE_NUMBER",
                                            "id": "wamid.ID",
                                            "timestamp": "TIMESTAMP",
                                            "text": {"body": "MESSAGE_BODY"},
                                            "type": "text",
                                        }
                                    ],
                                },
                                "field": "messages",
                            }
                        ],
                    }
                ],
            },
            whatsapp.payloads.TextMessage(
                text="MESSAGE_BODY", phone_number_id="123", wa_id="PHONE_NUMBER"
            ),
        )
    ],
)
def test_identify_payload(
    payload: JsonResponse, expected: whatsapp.payloads.TextMessage
) -> None:
    assert whatsapp.payloads.identify_payload(payload=payload).unwrap() == expected
