"""CLI entrypoint."""

from __future__ import annotations

import click

from customer_engine_api.cli import server

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(None, "-v", "--version")
def cli() -> None:
    """
    Customer Engine CLI.

    Developer tools.
    """  # noqa: D401


cli.add_command(cmd=server.cli)
