"""CLI integration for gravity analysis."""
from __future__ import annotations

from typing import List

import click

from envdiff.comparator import DiffResult
from envdiff.differ_gravity import GravityReport, gravity_diff


def _format_report(report: GravityReport, *, heavy_only: bool, top_n: int) -> str:
    entries = report.top(top_n) if top_n > 0 else report.entries
    if heavy_only:
        entries = [e for e in entries if e.is_heavy]
    if not entries:
        return "No gravity entries to display."
    lines = ["Gravity Report", "-" * 40]
    for e in entries:
        flag = " [HEAVY]" if e.is_heavy else ""
        lines.append(
            f"  {e.key:<30} score={e.gravity_score:.2f}  "
            f"issues={e.issues}/{e.total}{flag}"
        )
    return "\n".join(lines)


def gravity_options(f):
    f = click.option(
        "--gravity",
        is_flag=True,
        default=False,
        help="Show gravity analysis across multiple diff results.",
    )(f)
    f = click.option(
        "--gravity-heavy-only",
        is_flag=True,
        default=False,
        help="Only show keys with gravity score >= 0.5.",
    )(f)
    f = click.option(
        "--gravity-top",
        default=0,
        type=int,
        help="Limit output to top N keys by gravity score (0 = all).",
    )(f)
    return f


def apply_gravity(
    results: List[DiffResult],
    *,
    gravity: bool,
    gravity_heavy_only: bool,
    gravity_top: int,
) -> bool:
    """Compute and print gravity report. Returns True if flag was active."""
    if not gravity:
        return False
    report = gravity_diff(results)
    click.echo(_format_report(report, heavy_only=gravity_heavy_only, top_n=gravity_top))
    return True
