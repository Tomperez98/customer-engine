"""HTMX route."""

from __future__ import annotations

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse  # noqa: TCH002
from pydantic import BaseModel

from customer_engine_api.core.config import resources
from customer_engine_api.core.logging import logger

router = APIRouter(prefix="/htmx", tags=["htmx"])


@router.get("")
def index(req: Request) -> HTMLResponse:  # noqa: D103
    return resources.templates.TemplateResponse(request=req, name="index.html")


@router.post("/search")
def search(  # noqa: D103
    req: Request, name: str = Form(), last_name: str = Form(), email: str = Form()
) -> HTMLResponse:
    logger.info(name)
    logger.info(last_name)
    logger.info(email)
    return resources.templates.TemplateResponse(
        request=req, name="search-result.html", context={"result": "sd"}
    )


class User(BaseModel):  # noqa: D101
    first_name: str
    last_name: str


@router.get("/user-list")
def htmx_or_data(req: Request) -> HTMLResponse:
    """This route can serve both JSON and HTML, depending on if the request is an HTMX request or not."""  # noqa: D401, D404
    return resources.templates.TemplateResponse(
        request=req,
        name="user-list.html",
        context={
            "items": (
                User(first_name="Peter", last_name="Volf"),
                User(first_name="Hasan", last_name="Tasan"),
            )
        },
    )
