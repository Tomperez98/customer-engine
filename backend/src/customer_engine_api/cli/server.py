"""Server CLI group."""

from __future__ import annotations

import subprocess

import click


@click.group(name="server")
def cli() -> None:
    """Server subcommand."""


@cli.command()
@click.option(
    "-p",
    "--port",
    "port",
    help="Port number to expose the server.",
    required=True,
    type=click.IntRange(min=0, min_open=False),
)
def up(port: int) -> None:
    """Spin up the server."""
    subprocess.run(
        args=[
            "uvicorn",
            "customer_engine_api.api:app",
            "--reload",
            "--port",
            f"{port}",
        ],
        check=False,
    )
