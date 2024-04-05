from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, final

from lego_workflows.components import DomainError

if TYPE_CHECKING:
    from customer_engine_api.core.typing import Json, JsonResponse


class NotIdentifiedWhatsappPayloadError(DomainError):
    def __init__(self) -> None:
        super().__init__("An undentified whatsapp payloads has been received")


@final
@dataclass(frozen=True)
class _CommonInfo:
    phone_number_id: str


@final
@dataclass(frozen=True)
class TextMessage:
    text: str
    phone_number_id: str
    wa_id: str


def _process_common_and_get_specific_payload(
    payload: Json,
) -> tuple[_CommonInfo, JsonResponse]:
    value: Json = payload["entry"][0]["changes"][0].pop("value")
    value.pop("messaging_product")
    metadata: Json = value.pop("metadata")
    return (_CommonInfo(phone_number_id=metadata["phone_number_id"]), value)


def identify_payload(
    payload: JsonResponse,
) -> TextMessage:
    if isinstance(payload, list):
        raise NotIdentifiedWhatsappPayloadError

    common_info, specific_payload = _process_common_and_get_specific_payload(
        payload=payload
    )
    if isinstance(specific_payload, list):
        raise NotIdentifiedWhatsappPayloadError

    try:
        return TextMessage(
            text=specific_payload["messages"][0]["text"]["body"],
            wa_id=specific_payload["contacts"][0]["wa_id"],
            phone_number_id=common_info.phone_number_id,
        )

    except Exception as e:  # noqa: BLE001
        raise NotIdentifiedWhatsappPayloadError from e
