"""CLI extension: --multi flag to compare 3+ env files."""
from __future__ import annotations

import sys
import click

from envdiff.differ import multi_diff
from envdiff.formatter_multi import format_multi_text, format_multi_summary


def multi_options(cmd: click.Command) -> click.Command:
    """Decorator that adds --multi and --summary flags."""
    cmd = click.option(
        "--multi",
        "extra_files",
        multiple=True,
        metavar="FILE",
        help="Additional .env files to include in multi-file diff.",
    )(cmd)
    cmd = click.option(
        "--summary",
        is_flag=True,
        default=False,
        help="Print one-line summary per pair instead of full table.",
    )(cmd)
    return cmd


def apply_multi(
    file_a: str,
    file_b: str,
    extra_files: tuple,
    summary: bool,
    exit_code: bool,
) -> int:
    """Run multi-file diff and return exit code."""
    all_files = (file_a, file_b) + extra_files
    result = multi_diff(*all_files)

    if summary:
        click.echo(format_multi_summary(result), nl=False)
    else:
        click.echo(format_multi_text(result), nl=False)

    if exit_code and result.differing_keys:
        return 1
    return 0
