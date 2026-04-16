"""CLI option to rank keys by diff frequency across multiple env file pairs."""
from __future__ import annotations

import click

from envdiff.differ_rank import format_rank, rank_diffs


def rank_options(f):
    f = click.option(
        "--rank",
        is_flag=True,
        default=False,
        help="Rank keys by how often they appear as diffs.",
    )(f)
    return f


def apply_rank(results, rank: bool) -> None:
    """If --rank is set, print a ranked key report and return True (handled)."""
    if not rank:
        return
    report = rank_diffs(results)
    click.echo(format_rank(report))
