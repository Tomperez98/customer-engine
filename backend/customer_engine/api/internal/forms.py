"""form routes."""
from __future__ import annotations

import datetime
from typing import TypeAlias
from uuid import UUID

import lego_workflows
from fastapi import APIRouter
from mashumaro.codecs.orjson import ORJSONDecoder
from pydantic import AnyHttpUrl, BaseModel, Field, TypeAdapter

from customer_engine.core import global_config
from customer_engine.core.forms import Form, FormConfig
from customer_engine.core.transactions import SqlAlchemyTransactionCommiter

router = APIRouter(prefix="/forms", tags=["forms"])


class InternalUrlForm(BaseModel):  # noqa: D101
    url: AnyHttpUrl


class InternalWhatsAppFlowForm(BaseModel):  # noqa: D101
    flow_id: str


InternalFormConfiguration: TypeAlias = InternalUrlForm | InternalWhatsAppFlowForm


class InternalGetMostRelevantFormResponse(BaseModel):
    """Get most relevant points response."""

    most_relevant: Form
    configuration: InternalFormConfiguration


@router.get("/most-relevant")
async def get_most_relevant(prompt: str) -> InternalGetMostRelevantFormResponse:
    """Get most relevant forms flows."""
    from customer_engine.workflows.forms import get_most_relevant_form

    with global_config.db_engine.begin() as conn:
        response = await lego_workflows.execute(
            cmd=get_most_relevant_form.Command(
                org_code=global_config.default_org, prompt=prompt, conn=conn
            ),
            transaction_commiter=None,
        )

    return InternalGetMostRelevantFormResponse(
        most_relevant=response.most_revelant,
        configuration=TypeAdapter(InternalFormConfiguration).validate_python(
            response.configuration.to_dict()
        ),
    )


class InternalRegisterForm(BaseModel):  # noqa: D101
    name: str = Field(max_length=40)
    description: str = Field(max_length=200)
    configuration: InternalUrlForm | InternalWhatsAppFlowForm


class InternalRegisterFormResponse(BaseModel):  # noqa: D101
    form_id: UUID
    registed_at: datetime.datetime


@router.post("")
async def register_form(
    req: InternalRegisterForm,
) -> InternalRegisterFormResponse:
    """Register forms flow."""
    from customer_engine.workflows.forms import register_form

    with global_config.db_engine.begin() as conn:
        response = await lego_workflows.execute(
            register_form.Command(
                org_code=global_config.default_org,
                name=req.name,
                description=req.description,
                conn=conn,
                configuration=ORJSONDecoder(FormConfig).decode(
                    req.configuration.model_dump_json()
                ),
            ),
            transaction_commiter=SqlAlchemyTransactionCommiter(conn=conn),
        )

    return InternalRegisterFormResponse(
        registed_at=response.register_at, form_id=response.form_id
    )


class GetFormResponse(BaseModel):
    """Response to get forms flow."""

    form_id: UUID
    name: str
    description: str
    configuration: FormConfig


@router.get("/{form_id}")
async def get_forms_flow(form_id: UUID) -> GetFormResponse:
    """Get forms flow."""
    from customer_engine.workflows.forms import get_form

    with global_config.db_engine.begin() as conn:
        response = await lego_workflows.execute(
            get_form.Command(
                org_code=global_config.default_org,
                form_id=form_id,
                conn=conn,
            ),
            transaction_commiter=None,
        )

    return GetFormResponse(
        form_id=response.form.form_id,
        name=response.form.name,
        description=response.form.description,
        configuration=response.configuration,
    )


class GetAllFormsElement(BaseModel):
    """Element of get all forms."""

    form_id: UUID
    name: str
    description: str


class GetAllFormsResponse(BaseModel):  # noqa: D101
    flows: list[GetAllFormsElement]


@router.get("")
async def get_all_forms_flows() -> GetAllFormsResponse:
    """Get all forms flows."""
    from customer_engine.workflows.forms import get_all_forms

    with global_config.db_engine.begin() as conn:
        all_flows = await lego_workflows.execute(
            get_all_forms.Command(
                conn=conn,
                org_code=global_config.default_org,
            ),
            transaction_commiter=None,
        )

    return GetAllFormsResponse(
        flows=[
            GetAllFormsElement(
                form_id=flow.form_id,
                name=flow.name,
                description=flow.description,
            )
            for flow in all_flows.flows
        ]
    )


class DeleteFormResponse(BaseModel):
    """Response data to delete forms flow."""

    deleted_at: datetime.datetime


@router.delete("/{form_id}")
async def delte_form(form_id: UUID) -> DeleteFormResponse:
    """Delete forms flow."""
    from customer_engine.workflows.forms import delete_form

    with global_config.db_engine.begin() as conn:
        response = await lego_workflows.execute(
            delete_form.Command(
                org_code=global_config.default_org,
                form_id=form_id,
                conn=conn,
            ),
            transaction_commiter=SqlAlchemyTransactionCommiter(conn=conn),
        )

    return DeleteFormResponse(deleted_at=response.deleted_at)


class PatchForm(BaseModel):
    """Pathc forms flow request."""

    name: str | None = Field(max_length=40)
    description: str | None = Field(max_length=200)


class PathFormResponse(BaseModel):
    """Response to patch form."""

    form_id: UUID
    name: str
    description: str


@router.patch("/{form_id}")
async def path_form(form_id: UUID, patch_data: PatchForm) -> PathFormResponse:
    """Patch forms flow."""
    from customer_engine.workflows.forms import update_form

    with global_config.db_engine.begin() as conn:
        response = await lego_workflows.execute(
            update_form.Command(
                org_code=global_config.default_org,
                form_id=form_id,
                conn=conn,
                name=patch_data.name,
                description=patch_data.description,
            ),
            transaction_commiter=SqlAlchemyTransactionCommiter(conn=conn),
        )

    return PathFormResponse(
        form_id=response.flow.form_id,
        name=response.flow.name,
        description=response.flow.description,
    )
