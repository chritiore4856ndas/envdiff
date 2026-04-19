"""CLI integration for differ_velocity."""
from __future__ import annotations
import click
from typing import List
from envdiff.comparator import DiffResult
from envdiff.differ_velocity import velocity_results


def velocity_options(func):
    func = click.option(
        "--velocity", is_flag=True, default=False,
        help="Show key change velocity across multiple diff results."
    )(func)
    func = click.option(
        "--velocity-top", default=10, show_default=True,
        help="Number of top volatile keys to display."
    )(func)
    return func


def apply_velocity(results: List[DiffResult], velocity: bool, velocity_top: int) -> bool:
    """Print velocity report if --velocity flag is set. Returns True if printed."""
    if not velocity:
        return False

    report = velocity_results(results)
    fastest = report.fastest(velocity_top)

    if not fastest:
        click.echo("velocity: no differing keys found.")
        return True

    click.echo(f"{'Key':<40} {'Changes':>8} {'Rate':>8}")
    click.echo("-" * 60)
    for entry in fastest:
        click.echo(f"{entry.key:<40} {entry.change_count:>8} {entry.rate:>8.2f}")

    return True
