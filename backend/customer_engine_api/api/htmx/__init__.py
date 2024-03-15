"""HTMX route."""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fasthx import Jinja

router = APIRouter(prefix="/htmx", tags=["htmx"])
jinja = Jinja(Jinja2Templates("templates"))


@router.get("/")
@jinja.page("index.html")
def index() -> None: ...


@dataclass(frozen=True)
class User:
    first_name: str
    last_name: str


@router.get("/user-list")
@jinja.hx("user-list.html")
def htmx_or_data() -> tuple[User, ...]:
    """This route can serve both JSON and HTML, depending on if the request is an HTMX request or not."""
    return (
        User(first_name="Peter", last_name="Volf"),
        User(first_name="Hasan", last_name="Tasan"),
    )
