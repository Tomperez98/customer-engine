"""OpenAI third party client."""
from __future__ import annotations

from typing import Literal

import httpx


class OpenAI:
    """OpenAI Client."""

    def __init__(self, api_key: str) -> None:
        """Create a new instance of open ai client."""
        self._http_client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {api_key}"},
            base_url="https://api.openai.com",
        )

    async def most_relevant_whatsapp_workflows(
        self,
        id_description_pair: list[tuple[str, str]],
        prompt: str,
        model: Literal["gpt-3.5-turbo-0125"],
    ) -> str:
        """Get the most relevant whatsapp workflows for a given prompt."""
        response = await self._http_client.post(
            url="/v1/chat/completions",
            json={
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": """You are an assistant that tries to understand the need from a user to the form whose description matches the most.
                        In the event that you don't have enough context feel free to ask relevent questions to understand the user better.
                        Make sure the conversation is short.
                        """,
                    },
                    {
                        "role": "user",
                        "content": _whatsapp_workflows_user_content(
                            id_description_pair=id_description_pair, prompt=prompt
                        ),
                    },
                ],
            },
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]


def _whatsapp_workflows_user_content(
    id_description_pair: list[tuple[str, str]], prompt: str
) -> str:
    all_flows = "\n".join(
        (
            f"  - {flow_id}: {description}"
            for flow_id, description in id_description_pair
        )
    )

    return f"""Based on this requirement:
{prompt}
Which of the following form should I do?
{all_flows}"""
