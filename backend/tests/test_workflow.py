from __future__ import annotations

from uuid import UUID, uuid4

import lego_workflows
import pytest

from customer_engine.core import global_config
from customer_engine.core.transactions import SqlAlchemyTransactionCommiter
from customer_engine.workflows.forms import (
    delete_form,
    get_all_forms,
    get_form,
    register_form,
    update_form,
)


@pytest.mark.e2e()
async def test_retrieve_multiple() -> None:
    with global_config.db_engine.connect() as conn:
        test_ids: list[UUID] = [uuid4() for _ in range(2)]

        for form_id in test_ids:
            await lego_workflows.execute(
                register_form.Command(
                    name=f"{form_id} name",
                    description=f"{form_id} description",
                    conn=conn,
                    org_code="test",
                ),
                transaction_commiter=SqlAlchemyTransactionCommiter(conn=conn),
            )

        all_workflows = await lego_workflows.execute(
            get_all_forms.Command(conn=conn, org_code="test"),
            transaction_commiter=None,
        )

        assert len(all_workflows.flows) >= 2  # noqa: PLR2004
        all_ids: set[UUID] = {flow.form_id for flow in all_workflows.flows}
        for form_id in all_ids:
            assert form_id in all_ids

        for form_id in all_ids:
            await lego_workflows.execute(
                delete_form.Command(form_id=form_id, conn=conn, org_code="test"),
                transaction_commiter=SqlAlchemyTransactionCommiter(conn=conn),
            )


@pytest.mark.e2e()
async def test_update_flow() -> None:
    with global_config.db_engine.connect() as conn:
        created_flow = await lego_workflows.execute(
            register_form.Command(
                name="Initial Name",
                description="Initial Description",
                conn=conn,
                org_code="test",
            ),
            transaction_commiter=SqlAlchemyTransactionCommiter(conn=conn),
        )
        updated_workflow = await lego_workflows.execute(
            update_form.Command(
                form_id=created_flow.form_id,
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
            update_form.Command(
                form_id=created_flow.form_id,
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
            delete_form.Command(
                form_id=created_flow.form_id, conn=conn, org_code="test"
            ),
            transaction_commiter=SqlAlchemyTransactionCommiter(conn=conn),
        )


@pytest.mark.e2e()
async def test_delete_not_existing_flow() -> None:
    not_existing_flow_id = uuid4()
    with global_config.db_engine.connect() as conn, pytest.raises(
        get_form.FormsNotFoundError
    ):
        await lego_workflows.execute(
            delete_form.Command(
                form_id=not_existing_flow_id, conn=conn, org_code="test"
            ),
            transaction_commiter=SqlAlchemyTransactionCommiter(conn=conn),
        )


@pytest.mark.e2e()
async def test_create_and_delete_flow() -> None:
    with global_config.db_engine.connect() as conn:
        new_flow = await lego_workflows.execute(
            cmd=register_form.Command(
                name="Test Flow",
                description="Flow used for testing purposes.",
                conn=conn,
                org_code="test",
            ),
            transaction_commiter=SqlAlchemyTransactionCommiter(conn=conn),
        )

        response = await lego_workflows.execute(
            cmd=get_form.Command(form_id=new_flow.form_id, conn=conn, org_code="test"),
            transaction_commiter=None,
        )

        assert response.flow.form_id == new_flow.form_id

        await lego_workflows.execute(
            cmd=delete_form.Command(
                form_id=new_flow.form_id, conn=conn, org_code="test"
            ),
            transaction_commiter=SqlAlchemyTransactionCommiter(conn=conn),
        )

    with global_config.db_engine.connect() as conn, pytest.raises(
        get_form.FormsNotFoundError
    ):
        response = await lego_workflows.execute(
            cmd=get_form.Command(form_id=new_flow.form_id, conn=conn, org_code="test"),
            transaction_commiter=None,
        )
