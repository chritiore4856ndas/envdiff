"""CLI integration for maturity analysis."""
from __future__ import annotations

from typing import List, Tuple

import click

from envdiff.comparator import DiffResult
from envdiff.differ_maturity import MaturityReport, maturity_diff


def _format_report(report: MaturityReport, *, show_mature: bool = False) -> str:
    lines: List[str] = []
    entries = report.entries if show_mature else report.immature()
    if not entries:
        lines.append("  All keys are mature.")
        return "\n".join(lines)
    for entry in entries:
        flag = "mature" if entry.is_mature else "immature"
        lines.append(
            f"  {entry.key:<30} rate={entry.maturity_rate:.2f}  "
            f"stable={entry.stable_count}/{entry.total}  [{flag}]"
        )
    lines.append(f"\n  average maturity rate: {report.average_rate:.2f}")
    return "\n".join(lines)


def maturity_options(f):
    f = click.option(
        "--maturity",
        is_flag=True,
        default=False,
        help="Show key maturity analysis across multiple diff results.",
    )(f)
    f = click.option(
        "--maturity-show-mature",
        is_flag=True,
        default=False,
        help="Include mature (stable) keys in maturity output.",
    )(f)
    return f


def apply_maturity(
    results: List[DiffResult],
    maturity: bool,
    maturity_show_mature: bool,
) -> bool:
    """Run maturity analysis and print results.  Returns True if flag was active."""
    if not maturity:
        return False
    report = maturity_diff(results)
    click.echo("\nMaturity Analysis:")
    click.echo(_format_report(report, show_mature=maturity_show_mature))
    return True
