from __future__ import annotations

from uuid import uuid4

import lego_workflows
import pytest

from customer_engine.core import global_config
from customer_engine.core.transactions import SqlAlchemyTransactionCommiter
from customer_engine.workflows.whatsapp import (
    delete_flow,
    get_all_flows,
    get_flow,
    register_flow,
    update_flow,
)


@pytest.mark.e2e()
async def test_retrieve_multiple() -> None:
    with global_config.db_engine.begin() as conn:
        test_ids: list[str] = [f"{i}" for i in range(2)]

        for flow_id in test_ids:
            await lego_workflows.execute(
                register_flow.RegisterFlowCommand(
                    flow_id=flow_id,
                    name=f"{flow_id} name",
                    description=f"{flow_id} description",
                    metadata={},
                    conn=conn,
                ),
                transaction_commiter=SqlAlchemyTransactionCommiter(conn=conn),
            )

        all_workflows = await lego_workflows.execute(
            get_all_flows.GetAllWhatsAppFlowsCommand(conn=conn),
            transaction_commiter=SqlAlchemyTransactionCommiter(conn=conn),
        )

        assert len(all_workflows.flows) >= 2  # noqa: PLR2004
        all_ids: set[str] = {flow.flow_id for flow in all_workflows.flows}
        for flow_id in all_ids:
            assert flow_id in all_ids

        for flow_id in all_ids:
            await lego_workflows.execute(
                delete_flow.DeleteFlow(flow_id=flow_id, conn=conn),
                transaction_commiter=SqlAlchemyTransactionCommiter(conn=conn),
            )


@pytest.mark.e2e()
async def test_update_flow() -> None:
    flow_id = uuid4().hex
    with global_config.db_engine.begin() as conn:
        await lego_workflows.execute(
            register_flow.RegisterFlowCommand(
                flow_id=flow_id,
                name="Initial Name",
                description="Initial Description",
                conn=conn,
                metadata={},
            ),
            transaction_commiter=SqlAlchemyTransactionCommiter(conn=conn),
        )
        updated_workflow = await lego_workflows.execute(
            update_flow.UpdateWhatsAppFlowCommand(
                flow_id=flow_id,
                name="New Name",
                description="New description",
                conn=conn,
            ),
            transaction_commiter=SqlAlchemyTransactionCommiter(conn=conn),
        )

        assert updated_workflow.flow.name == "New Name"
        assert updated_workflow.flow.description == "New description"

        updated_workflow = await lego_workflows.execute(
            update_flow.UpdateWhatsAppFlowCommand(
                flow_id=flow_id,
                name=None,
                description="New description v2",
                conn=conn,
            ),
            transaction_commiter=SqlAlchemyTransactionCommiter(conn=conn),
        )

        assert updated_workflow.flow.name == "New Name"
        assert updated_workflow.flow.description == "New description v2"

        await lego_workflows.execute(
            delete_flow.DeleteFlow(flow_id=flow_id, conn=conn),
            transaction_commiter=SqlAlchemyTransactionCommiter(conn=conn),
        )


@pytest.mark.e2e()
async def test_delete_not_existing_flow() -> None:
    with global_config.db_engine.begin() as conn, pytest.raises(
        get_flow.WhatsAppFlowNotFoundError
    ):
        await lego_workflows.execute(
            delete_flow.DeleteFlow(flow_id="NOT EXISTING", conn=conn),
            transaction_commiter=SqlAlchemyTransactionCommiter(conn=conn),
        )


@pytest.mark.e2e()
async def test_create_and_delete_flow() -> None:
    with global_config.db_engine.begin() as conn:
        await lego_workflows.execute(
            cmd=register_flow.RegisterFlowCommand(
                flow_id="123",
                name="Test Flow",
                description="Flow used for testing purposes.",
                conn=conn,
                metadata={"country": "COL"},
            ),
            transaction_commiter=SqlAlchemyTransactionCommiter(conn=conn),
        )

        response = await lego_workflows.execute(
            cmd=get_flow.GetFlowCommand(flow_id="123", conn=conn),
            transaction_commiter=SqlAlchemyTransactionCommiter(conn=conn),
        )

        assert response.flow.flow_id == "123"

        await lego_workflows.execute(
            cmd=delete_flow.DeleteFlow(flow_id="123", conn=conn),
            transaction_commiter=SqlAlchemyTransactionCommiter(conn=conn),
        )

    with global_config.db_engine.begin() as conn, pytest.raises(
        get_flow.WhatsAppFlowNotFoundError
    ):
        response = await lego_workflows.execute(
            cmd=get_flow.GetFlowCommand(flow_id="123", conn=conn),
            transaction_commiter=SqlAlchemyTransactionCommiter(conn=conn),
        )
