"""CLI integration for the dispersion analyser."""
from __future__ import annotations

from typing import List

import click

from envdiff.comparator import DiffResult
from envdiff.differ_dispersion import DispersionReport, dispersion_diff


def _format_report(report: DispersionReport, threshold: float) -> str:
    spread = report.spread(threshold=threshold)
    if not spread:
        return "dispersion: no keys spread above threshold"
    lines = [f"dispersion report ({report.total_snapshots} snapshots):"]
    for entry in spread:
        lines.append(
            f"  {entry.key}: {entry.appearances}/{entry.total} "
            f"({entry.dispersion_rate:.0%})"
        )
    return "\n".join(lines)


def dispersion_options(f):
    f = click.option(
        "--dispersion",
        is_flag=True,
        default=False,
        help="Show key-dispersion analysis across multiple diff results.",
    )(f)
    f = click.option(
        "--dispersion-threshold",
        "dispersion_threshold",
        type=float,
        default=0.5,
        show_default=True,
        help="Minimum dispersion rate to include in output.",
    )(f)
    return f


def apply_dispersion(
    results: List[DiffResult],
    dispersion: bool,
    dispersion_threshold: float,
) -> bool:
    """Run dispersion analysis and print results.  Returns True when active."""
    if not dispersion:
        return False
    report = dispersion_diff(results)
    click.echo(_format_report(report, threshold=dispersion_threshold))
    return True
