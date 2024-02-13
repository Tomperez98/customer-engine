from __future__ import annotations

import lego_workflows

from customer_engine.workflows.hello_word import HelloWorld


async def test_execution() -> None:
    await lego_workflows.execute(HelloWorld(), transaction_commiter=None)
