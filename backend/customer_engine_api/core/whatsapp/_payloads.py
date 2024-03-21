from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, final

from lego_workflows.components import DomainError
from result import Err, Ok

if TYPE_CHECKING:
    from result import Result

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
) -> Result[TextMessage, NotIdentifiedWhatsappPayloadError]:
    if isinstance(payload, list):
        return Err(NotIdentifiedWhatsappPayloadError())

    common_info, specific_payload = _process_common_and_get_specific_payload(
        payload=payload
    )
    if isinstance(specific_payload, list):
        return Err(NotIdentifiedWhatsappPayloadError())

    try:
        return Ok(
            TextMessage(
                text=specific_payload["messages"][0]["text"]["body"],
                wa_id=specific_payload["contacts"][0]["wa_id"],
                phone_number_id=common_info.phone_number_id,
            )
        )
    except Exception:  # noqa: BLE001
        return Err(NotIdentifiedWhatsappPayloadError())
