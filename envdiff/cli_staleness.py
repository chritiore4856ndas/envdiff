"""CLI integration for staleness detection."""
from __future__ import annotations
import click
from typing import List
from envdiff.comparator import DiffResult
from envdiff.differ_staleness import staleness_diff


def staleness_options(f):
    f = click.option(
        "--staleness",
        is_flag=True,
        default=False,
        help="Show keys that are unchanged across all compared snapshots.",
    )(f)
    f = click.option(
        "--staleness-only",
        is_flag=True,
        default=False,
        help="Only print stale keys, suppress active ones.",
    )(f)
    return f


def apply_staleness(results: List[DiffResult], staleness: bool, staleness_only: bool) -> bool:
    """Run staleness analysis and print results. Returns True if stale keys found."""
    if not staleness:
        return False

    report = staleness_diff(results)

    if not report.entries:
        click.echo("staleness: no keys tracked")
        return False

    entries = report.stale() if staleness_only else report.entries

    click.echo("\n=== Staleness Report ===")
    for entry in entries:
        status = "STALE" if entry.is_stale else "active"
        value_display = repr(entry.value) if entry.value is not None else "(missing)"
        click.echo(f"  {entry.key:<30} {status:<8} seen={entry.snapshots_seen}  value={value_display}")

    stale_count = len(report.stale())
    click.echo(f"\n{stale_count}/{len(report.entries)} keys are stale.")
    return stale_count > 0
