"""whatsapp routes."""
from __future__ import annotations

import datetime
from uuid import UUID

import lego_workflows
from fastapi import APIRouter
from pydantic import BaseModel, Field

from customer_engine.core import global_config
from customer_engine.core.transactions import SqlAlchemyTransactionCommiter

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])


class RegisterWhatsAppFlow(BaseModel):  # noqa: D101
    name: str = Field(max_length=40)
    description: str = Field(max_length=200)


class RegisterWhatsAppFlowResponse(BaseModel):  # noqa: D101
    flow_id: UUID
    registed_at: datetime.datetime


@router.post("/flows")
async def register_whatsapp_flow(
    req: RegisterWhatsAppFlow,
) -> RegisterWhatsAppFlowResponse:
    """Register whatsapp flow."""
    from customer_engine.workflows.whatsapp import register_flow

    with global_config.db_engine.begin() as conn:
        response = await lego_workflows.execute(
            register_flow.RegisterFlowCommand(
                org_code=global_config.default_org,
                name=req.name,
                description=req.description,
                conn=conn,
            ),
            transaction_commiter=SqlAlchemyTransactionCommiter(conn=conn),
        )

    return RegisterWhatsAppFlowResponse(
        registed_at=response.register_at, flow_id=response.flow_id
    )


class GetWhatsAppFlowResponse(BaseModel):
    """Response to get whatsapp flow."""

    flow_id: UUID
    name: str
    description: str


@router.get("/flows/{flow_id}")
async def get_whatsapp_flow(flow_id: UUID) -> GetWhatsAppFlowResponse:
    """Get whatsapp flow."""
    from customer_engine.workflows.whatsapp import get_flow

    with global_config.db_engine.begin() as conn:
        response = await lego_workflows.execute(
            get_flow.GetFlowCommand(
                org_code=global_config.default_org,
                flow_id=flow_id,
                conn=conn,
            ),
            transaction_commiter=SqlAlchemyTransactionCommiter(conn=conn),
        )

    return GetWhatsAppFlowResponse(
        flow_id=response.flow.flow_id,
        name=response.flow.name,
        description=response.flow.description,
    )


class GetAllWhatsAppFlowsResponse(BaseModel):  # noqa: D101
    flows: list[GetWhatsAppFlowResponse]


@router.get("/flows")
async def get_all_whatsapp_flows() -> GetAllWhatsAppFlowsResponse:
    """Get all whatsapp flows."""
    from customer_engine.workflows.whatsapp import get_all_flows

    with global_config.db_engine.begin() as conn:
        all_flows = await lego_workflows.execute(
            get_all_flows.GetAllWhatsAppFlowsCommand(
                conn=conn,
                org_code=global_config.default_org,
            ),
            transaction_commiter=SqlAlchemyTransactionCommiter(conn=conn),
        )

    return GetAllWhatsAppFlowsResponse(
        flows=[
            GetWhatsAppFlowResponse(
                flow_id=flow.flow_id,
                name=flow.name,
                description=flow.description,
            )
            for flow in all_flows.flows
        ]
    )


class DeleteWhatsAppFlowResponse(BaseModel):
    """Response data to delete whatsapp flow."""

    deleted_at: datetime.datetime


@router.delete("/flows/{flow_id}")
async def delete_whatsapp_flow(flow_id: UUID) -> DeleteWhatsAppFlowResponse:
    """Delete whatsapp flow."""
    from customer_engine.workflows.whatsapp import delete_flow

    with global_config.db_engine.begin() as conn:
        response = await lego_workflows.execute(
            delete_flow.DeleteFlow(
                org_code=global_config.default_org,
                flow_id=flow_id,
                conn=conn,
            ),
            transaction_commiter=SqlAlchemyTransactionCommiter(conn=conn),
        )

    return DeleteWhatsAppFlowResponse(deleted_at=response.deleted_at)


class PatchWhatsAppFlow(BaseModel):
    """Pathc whatsapp flow request."""

    name: str | None = Field(max_length=40)
    description: str | None = Field(max_length=200)


@router.patch("/flows/{flow_id}")
async def patch_whatsapp_flow(
    flow_id: UUID, patch_data: PatchWhatsAppFlow
) -> GetWhatsAppFlowResponse:
    """Patch whatsapp flow."""
    from customer_engine.workflows.whatsapp import update_flow

    with global_config.db_engine.begin() as conn:
        response = await lego_workflows.execute(
            update_flow.UpdateWhatsAppFlowCommand(
                org_code=global_config.default_org,
                flow_id=flow_id,
                conn=conn,
                name=patch_data.name,
                description=patch_data.description,
            ),
            transaction_commiter=SqlAlchemyTransactionCommiter(conn=conn),
        )

    return GetWhatsAppFlowResponse(
        flow_id=response.flow.flow_id,
        name=response.flow.name,
        description=response.flow.description,
    )
