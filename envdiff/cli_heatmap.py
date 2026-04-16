"""CLI option to display a heatmap of frequently differing keys."""
from __future__ import annotations

import click

from envdiff.differ_heatmap import build_heatmap


def heatmap_options(f):
    f = click.option(
        "--heatmap",
        is_flag=True,
        default=False,
        help="Show heatmap of most frequently differing keys.",
    )(f)
    f = click.option(
        "--heatmap-top",
        default=10,
        show_default=True,
        metavar="N",
        help="Number of top keys to show in heatmap.",
    )(f)
    return f


def apply_heatmap(results, heatmap: bool, heatmap_top: int) -> None:
    """Print heatmap if --heatmap flag is set."""
    if not heatmap:
        return

    report = build_heatmap(results)
    top = report.top(heatmap_top)

    if not top:
        click.echo("heatmap: no differing keys found")
        return

    click.echo("\n--- Key Diff Heatmap ---")
    for entry in top:
        bar = "#" * entry.count
        click.echo(f"  {entry.key:<30} {bar} ({entry.count})")
    click.echo("")
