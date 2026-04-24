"""CLI integration for differ_recurrence."""
from __future__ import annotations

from typing import List

import click

from envdiff.comparator import DiffResult
from envdiff.differ_recurrence import RecurrenceReport, recurrence_diff


def _format_report(report: RecurrenceReport, top: int) -> str:
    if not report.entries:
        return "No recurrent keys found."

    lines = [
        f"Recurrence report ({report.total_snapshots} snapshots):",
    ]
    for entry in report.top(top):
        flag = " [recurrent]" if entry.is_recurrent else ""
        lines.append(
            f"  {entry.key}: {entry.occurrences}/{entry.total} "
            f"({entry.recurrence_rate:.0%}){flag}"
        )
    return "\n".join(lines)


def recurrence_options(f):
    f = click.option(
        "--recurrence",
        is_flag=True,
        default=False,
        help="Show key recurrence report across results.",
    )(f)
    f = click.option(
        "--recurrence-top",
        "recurrence_top",
        default=10,
        show_default=True,
        type=int,
        help="Number of top recurrent keys to display.",
    )(f)
    return f


def apply_recurrence(
    results: List[DiffResult],
    recurrence: bool,
    recurrence_top: int,
) -> bool:
    """Print recurrence report if flag is set. Returns True if activated."""
    if not recurrence:
        return False

    report = recurrence_diff(results)
    click.echo(_format_report(report, top=recurrence_top))
    return True
