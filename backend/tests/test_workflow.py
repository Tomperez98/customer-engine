from __future__ import annotations

from uuid import UUID, uuid4

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
    with global_config.db_engine.connect() as conn:
        test_ids: list[UUID] = [uuid4() for _ in range(2)]

        for flow_id in test_ids:
            await lego_workflows.execute(
                register_flow.RegisterFlowCommand(
                    name=f"{flow_id} name",
                    description=f"{flow_id} description",
                    conn=conn,
                    org_code="test",
                ),
                transaction_commiter=SqlAlchemyTransactionCommiter(conn=conn),
            )

        all_workflows = await lego_workflows.execute(
            get_all_flows.GetAllWhatsAppFlowsCommand(conn=conn, org_code="test"),
            transaction_commiter=None,
        )

        assert len(all_workflows.flows) >= 2  # noqa: PLR2004
        all_ids: set[UUID] = {flow.flow_id for flow in all_workflows.flows}
        for flow_id in all_ids:
            assert flow_id in all_ids

        for flow_id in all_ids:
            await lego_workflows.execute(
                delete_flow.DeleteFlow(flow_id=flow_id, conn=conn, org_code="test"),
                transaction_commiter=SqlAlchemyTransactionCommiter(conn=conn),
            )


@pytest.mark.e2e()
async def test_update_flow() -> None:
    with global_config.db_engine.connect() as conn:
        created_flow = await lego_workflows.execute(
            register_flow.RegisterFlowCommand(
                name="Initial Name",
                description="Initial Description",
                conn=conn,
                org_code="test",
            ),
            transaction_commiter=SqlAlchemyTransactionCommiter(conn=conn),
        )
        updated_workflow = await lego_workflows.execute(
            update_flow.UpdateWhatsAppFlowCommand(
                flow_id=created_flow.flow_id,
                name="New Name",
                description="New description",
                conn=conn,
                org_code="test",
            ),
            transaction_commiter=SqlAlchemyTransactionCommiter(conn=conn),
        )

        assert updated_workflow.flow.name == "New Name"
        assert updated_workflow.flow.description == "New description"

        updated_workflow = await lego_workflows.execute(
            update_flow.UpdateWhatsAppFlowCommand(
                flow_id=created_flow.flow_id,
                name=None,
                description="New description v2",
                conn=conn,
                org_code="test",
            ),
            transaction_commiter=SqlAlchemyTransactionCommiter(conn=conn),
        )

        assert updated_workflow.flow.name == "New Name"
        assert updated_workflow.flow.description == "New description v2"

        await lego_workflows.execute(
            delete_flow.DeleteFlow(
                flow_id=created_flow.flow_id, conn=conn, org_code="test"
            ),
            transaction_commiter=SqlAlchemyTransactionCommiter(conn=conn),
        )


@pytest.mark.e2e()
async def test_delete_not_existing_flow() -> None:
    not_existing_flow_id = uuid4()
    with global_config.db_engine.connect() as conn, pytest.raises(
        get_flow.WhatsAppFlowNotFoundError
    ):
        await lego_workflows.execute(
            delete_flow.DeleteFlow(
                flow_id=not_existing_flow_id, conn=conn, org_code="test"
            ),
            transaction_commiter=SqlAlchemyTransactionCommiter(conn=conn),
        )


@pytest.mark.e2e()
async def test_create_and_delete_flow() -> None:
    with global_config.db_engine.connect() as conn:
        new_flow = await lego_workflows.execute(
            cmd=register_flow.RegisterFlowCommand(
                name="Test Flow",
                description="Flow used for testing purposes.",
                conn=conn,
                org_code="test",
            ),
            transaction_commiter=SqlAlchemyTransactionCommiter(conn=conn),
        )

        response = await lego_workflows.execute(
            cmd=get_flow.GetFlowCommand(
                flow_id=new_flow.flow_id, conn=conn, org_code="test"
            ),
            transaction_commiter=None,
        )

        assert response.flow.flow_id == new_flow.flow_id

        await lego_workflows.execute(
            cmd=delete_flow.DeleteFlow(
                flow_id=new_flow.flow_id, conn=conn, org_code="test"
            ),
            transaction_commiter=SqlAlchemyTransactionCommiter(conn=conn),
        )

    with global_config.db_engine.connect() as conn, pytest.raises(
        get_flow.WhatsAppFlowNotFoundError
    ):
        response = await lego_workflows.execute(
            cmd=get_flow.GetFlowCommand(
                flow_id=new_flow.flow_id, conn=conn, org_code="test"
            ),
            transaction_commiter=None,
        )
