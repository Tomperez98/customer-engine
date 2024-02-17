from __future__ import annotations

from uuid import UUID, uuid4

import lego_workflows
import pytest

from customer_engine.core import global_config
from customer_engine.core.forms import UrlForm, WhatsAppFlowForm
from customer_engine.workflows.forms import (
    delete_form,
    get_all_forms,
    get_form,
    get_most_relevant_form,
    register_form,
    update_form,
)


@pytest.mark.e2e()
async def test_retrieve_multiple() -> None:
    with global_config.db_engine.begin() as conn:
        test_ids: list[UUID] = [uuid4() for _ in range(2)]

        for form_id in test_ids:
            await lego_workflows.run_and_collect_events(
                register_form.Command(
                    name=f"{form_id} name",
                    description=f"{form_id} description",
                    conn=conn,
                    org_code="test",
                    configuration=UrlForm(url="https://google.com"),
                ),
            )

        all_workflows, _ = await lego_workflows.run_and_collect_events(
            get_all_forms.Command(conn=conn, org_code="test"),
        )

        assert len(all_workflows.flows) >= 2  # noqa: PLR2004
        all_ids: set[UUID] = {flow.form_id for flow in all_workflows.flows}
        for form_id in all_ids:
            assert form_id in all_ids

        for form_id in all_ids:
            await lego_workflows.run_and_collect_events(
                delete_form.Command(form_id=form_id, conn=conn, org_code="test"),
            )


@pytest.mark.e2e()
async def test_get_most_relevant() -> None:
    with global_config.db_engine.begin() as conn:
        first_flow, _ = await lego_workflows.run_and_collect_events(
            register_form.Command(
                org_code="test",
                conn=conn,
                name="Formulario Ofertas Laborales",
                description="Estoy buscando trabajo, me gustaria ver oportunidades de empleo, ofertas laborales",
                configuration=UrlForm(url="https://test.com"),
            ),
        )
        second_flow, _ = await lego_workflows.run_and_collect_events(
            register_form.Command(
                org_code="test",
                conn=conn,
                name="Formulario Reserva de restaurante",
                description="Me gustaria hacer una reserva para esta noche, quisiera conocer el restaurante",
                configuration=WhatsAppFlowForm(flow_id="HCSP"),
            ),
        )

        most_relevant_form, _ = await lego_workflows.run_and_collect_events(
            get_most_relevant_form.Command(
                org_code="test",
                prompt="Hola! Me gustaria conocer oportunidades de empleo",
                conn=conn,
            ),
        )
        assert isinstance(most_relevant_form.configuration, UrlForm)
        assert most_relevant_form.most_revelant.form_id == first_flow.form_id
        assert most_relevant_form.configuration.url == "https://test.com"

        most_relevant_form, _ = await lego_workflows.run_and_collect_events(
            get_most_relevant_form.Command(
                org_code="test",
                prompt="Hola! Para hacer una reserva esta noche en el restaurante de Manila",
                conn=conn,
            ),
        )

        assert isinstance(most_relevant_form.configuration, WhatsAppFlowForm)
        assert most_relevant_form.most_revelant.form_id == second_flow.form_id
        assert most_relevant_form.configuration.flow_id == "HCSP"

        await lego_workflows.run_and_collect_events(
            delete_form.Command(form_id=first_flow.form_id, org_code="test", conn=conn),
        )

        await lego_workflows.run_and_collect_events(
            delete_form.Command(
                form_id=second_flow.form_id, org_code="test", conn=conn
            ),
        )


@pytest.mark.e2e()
async def test_update_flow() -> None:
    with global_config.db_engine.begin() as conn:
        created_flow, _ = await lego_workflows.run_and_collect_events(
            register_form.Command(
                name="Initial Name",
                description="Initial Description",
                conn=conn,
                org_code="test",
                configuration=UrlForm(url="https://google.com"),
            ),
        )
        updated_workflow, _ = await lego_workflows.run_and_collect_events(
            update_form.Command(
                form_id=created_flow.form_id,
                name="New Name",
                description="New description",
                conn=conn,
                org_code="test",
            ),
        )

        assert updated_workflow.flow.name == "New Name"
        assert updated_workflow.flow.description == "New description"

        updated_workflow, _ = await lego_workflows.run_and_collect_events(
            update_form.Command(
                form_id=created_flow.form_id,
                name=None,
                description="New description v2",
                conn=conn,
                org_code="test",
            ),
        )

        assert updated_workflow.flow.name == "New Name"
        assert updated_workflow.flow.description == "New description v2"

        await lego_workflows.run_and_collect_events(
            delete_form.Command(
                form_id=created_flow.form_id, conn=conn, org_code="test"
            ),
        )


@pytest.mark.e2e()
async def test_delete_not_existing_flow() -> None:
    not_existing_flow_id = uuid4()
    with global_config.db_engine.begin() as conn, pytest.raises(
        get_form.FormNotFoundError
    ):
        await lego_workflows.run_and_collect_events(
            delete_form.Command(
                form_id=not_existing_flow_id, conn=conn, org_code="test"
            ),
        )


@pytest.mark.e2e()
async def test_create_and_delete_flow() -> None:
    with global_config.db_engine.begin() as conn:
        new_flow, _ = await lego_workflows.run_and_collect_events(
            cmd=register_form.Command(
                name="Test Flow",
                description="Flow used for testing purposes.",
                conn=conn,
                org_code="test",
                configuration=UrlForm(url="https://google.com"),
            ),
        )

        response, _ = await lego_workflows.run_and_collect_events(
            cmd=get_form.Command(form_id=new_flow.form_id, conn=conn, org_code="test"),
        )

        assert response.form.form_id == new_flow.form_id
        assert isinstance(response.configuration, UrlForm)

        await lego_workflows.run_and_collect_events(
            cmd=delete_form.Command(
                form_id=new_flow.form_id, conn=conn, org_code="test"
            ),
        )

    with global_config.db_engine.begin() as conn, pytest.raises(
        get_form.FormNotFoundError
    ):
        await lego_workflows.run_and_collect_events(
            cmd=get_form.Command(form_id=new_flow.form_id, conn=conn, org_code="test"),
        )
