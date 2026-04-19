"""CLI integration for variance reporting."""
from __future__ import annotations
import click
from typing import List
from envdiff.comparator import DiffResult
from envdiff.differ_variance import variance_diff


def variance_options(func):
    func = click.option(
        "--variance",
        is_flag=True,
        default=False,
        help="Show value variance across all compared env files.",
    )(func)
    func = click.option(
        "--variance-unstable-only",
        is_flag=True,
        default=False,
        help="Only show keys with varying values.",
    )(func)
    return func


def apply_variance(
    results: List[DiffResult],
    variance: bool,
    variance_unstable_only: bool,
) -> bool:
    """Print variance report. Returns True if any unstable keys found."""
    if not variance:
        return False

    report = variance_diff(results)
    entries = report.unstable() if variance_unstable_only else report.entries

    if not entries:
        click.echo("variance: all keys are stable")
        return False

    click.echo(f"variance report ({len(entries)} keys):")
    for entry in entries:
        status = "unstable" if not entry.is_stable else "stable"
        click.echo(f"  [{status}] {entry.key}  unique_values={entry.unique_count}")

    return len(report.unstable()) > 0
