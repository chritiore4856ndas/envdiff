"""Click option group that wires --export-format / --output into the CLI."""
from __future__ import annotations

import functools
import sys
from typing import Callable

import click

from envdiff.exporter import export_diff, ExportFormat
from envdiff.sorter import GroupedDiff


def export_options(fn: Callable) -> Callable:
    """Decorator that adds --export-format and --output options to a command."""
    fn = click.option(
        "--output",
        "-o",
        default=None,
        metavar="FILE",
        help="Write export output to FILE instead of stdout.",
    )(fn)
    fn = click.option(
        "--export-format",
        "export_format",
        type=click.Choice(["json", "csv", "markdown"]),
        default=None,
        help="Export diff in the given format and exit.",
    )(fn)
    return fn


def apply_export(
    grouped: GroupedDiff,
    export_format: str | None,
    output: str | None,
) -> bool:
    """If *export_format* is set, write the export and return True.

    Returns False when no export was requested so the caller can continue
    with normal text/JSON reporting.
    """
    if export_format is None:
        return False

    content = export_diff(grouped, export_format)  # type: ignore[arg-type]
    if output:
        with open(output, "w", encoding="utf-8") as fh:
            fh.write(content)
    else:
        click.echo(content, nl=False)
    return True
