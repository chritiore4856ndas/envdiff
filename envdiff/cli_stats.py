"""CLI integration for differ_stats — show aggregated key issue stats."""
from __future__ import annotations

import click

from envdiff.comparator import compare
from envdiff.differ_stats import compute_stats, format_stats
from envdiff.parser import parse_env_file


def stats_options(cmd):
    """Decorator that adds --stats flag to a command."""
    cmd = click.option(
        "--stats",
        is_flag=True,
        default=False,
        help="Show aggregated per-key issue statistics across all file pairs.",
    )(cmd)
    return cmd


def apply_stats(files: list[str], show: bool, ctx: click.Context) -> None:
    """Compare consecutive file pairs and print aggregated stats.

    files: flat list of paths; compared as (0,1), (1,2), ...
    """
    if not show:
        return

    if len(files) < 2:
        click.echo("stats: need at least two files to compare.", err=True)
        return

    results = []
    for i in range(len(files) - 1):
        a = parse_env_file(files[i])
        b = parse_env_file(files[i + 1])
        results.append(compare(a, b))

    stats = compute_stats(results)
    click.echo(format_stats(stats))
