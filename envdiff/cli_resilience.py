"""CLI integration for resilience analysis."""
from __future__ import annotations

from typing import List, Tuple

import click

from envdiff.comparator import DiffResult
from envdiff.differ_resilience import ResilienceReport, resilience_diff


def _format_report(report: ResilienceReport, threshold: float, show_all: bool) -> str:
    if not report.entries:
        return "resilience: no data"

    lines = ["Resilience Report:", "-" * 40]
    entries = report.entries if show_all else report.fragile(threshold)
    if not entries:
        lines.append("  all keys meet resilience threshold")
    else:
        for e in entries:
            flag = "OK" if e.is_resilient(threshold) else "FRAGILE"
            lines.append(
                f"  {e.key:<30} rate={e.resilience_rate():.2f}  "
                f"issues={e.issue_count}/{e.total}  [{flag}]"
            )
    return "\n".join(lines)


def resilience_options(f):
    f = click.option(
        "--resilience",
        is_flag=True,
        default=False,
        help="Show resilience analysis across multiple diff results.",
    )(f)
    f = click.option(
        "--resilience-threshold",
        default=0.8,
        show_default=True,
        type=float,
        help="Minimum rate to consider a key resilient.",
    )(f)
    f = click.option(
        "--resilience-all",
        is_flag=True,
        default=False,
        help="Show all keys, not just fragile ones.",
    )(f)
    return f


def apply_resilience(
    results: List[DiffResult],
    resilience: bool,
    resilience_threshold: float,
    resilience_all: bool,
) -> bool:
    if not resilience:
        return False
    report = resilience_diff(results)
    click.echo(_format_report(report, resilience_threshold, resilience_all))
    return True
