"""CLI decorator that adds a --score flag to the main diff command."""

from __future__ import annotations

import functools
from typing import Callable

import click

from envdiff.comparator import DiffResult
from envdiff.scorer import format_score, score_diff


def score_options(cmd: Callable) -> Callable:
    """Attach --score option to a Click command."""

    @click.option(
        "--score",
        "show_score",
        is_flag=True,
        default=False,
        help="Print a similarity score after the diff.",
    )
    @functools.wraps(cmd)
    def wrapper(*args, show_score: bool = False, **kwargs):
        return cmd(*args, show_score=show_score, **kwargs)

    return wrapper


def apply_score(result: DiffResult, show_score: bool) -> None:
    """Print the score block to stdout when requested."""
    if not show_score:
        return
    score = score_diff(result)
    click.echo("")
    click.echo(format_score(score))
