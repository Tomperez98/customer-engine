from __future__ import annotations

import pytest

from customer_engine.core import global_config
from customer_engine.core.clients import open_ai


@pytest.mark.unit()
@pytest.mark.parametrize(
    argnames=["id_description_pair", "prompt", "expected"],
    argvalues=[
        (
            [
                ("ID1", "For client looking for investment oportunities"),
                ("ID1", "For client who want to summit a complain"),
            ],
            "I'll like to see the available invesment oportunities.",
            "Based on this requirement:\nI'll like to see the available invesment oportunities.\nWhich of the following form should I do?\n  - ID1: For client looking for investment oportunities\n  - ID1: For client who want to summit a complain",
        )
    ],
)
def test_whatsapp_workflows_user_content(
    id_description_pair: list[tuple[str, str]], prompt: str, expected: str
) -> None:
    assert (
        open_ai._whatsapp_workflows_user_content(
            id_description_pair=id_description_pair, prompt=prompt
        )
        == expected
    )


@pytest.mark.integration()
async def test_most_relevant_whatsapp_workflows() -> None:
    most_relevant_workflow = (
        await global_config.clients.openai.most_relevant_whatsapp_workflows(
            id_description_pair=[
                ("ID1", "For client looking for investment oportunities"),
                ("ID3", "For client who want to summit a complain"),
            ],
            prompt="I'll like to see the available invesment oportunities.",
            model="gpt-3.5-turbo-0125",
        )
    )
    assert most_relevant_workflow
