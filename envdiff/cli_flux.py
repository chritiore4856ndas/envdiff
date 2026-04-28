"""CLI integration for flux analysis."""
from __future__ import annotations

from typing import List, Tuple

import click

from envdiff.comparator import DiffResult
from envdiff.differ_flux import FluxReport, flux_diff


def _format_report(report: FluxReport, *, threshold: float = 0.5) -> str:
    lines = []
    for entry in report.entries:
        if entry.flux_rate >= threshold:
            flag = "[HIGH]" if entry.is_flux else "[LOW] "
            lines.append(
                f"  {flag} {entry.key}: rate={entry.flux_rate:.2f} "
                f"({entry.change_count}/{entry.total_transitions} transitions)"
            )
    if not lines:
        return "  (no keys above flux threshold)"
    return "\n".join(lines)


def flux_options(f):
    f = click.option(
        "--flux",
        is_flag=True,
        default=False,
        help="Show flux analysis across multiple diff results.",
    )(f)
    f = click.option(
        "--flux-threshold",
        default=0.5,
        show_default=True,
        type=float,
        help="Minimum flux rate to display (0.0–1.0).",
    )(f)
    return f


def apply_flux(
    results: List[DiffResult],
    flux: bool,
    flux_threshold: float,
) -> bool:
    """Run flux analysis and print report. Returns True if flag was active."""
    if not flux:
        return False

    report = flux_diff(results)
    click.echo("Flux Analysis:")
    click.echo(f"  Average flux rate : {report.average_flux:.2f}")
    most = report.most_volatile
    click.echo(f"  Most volatile key : {most.key if most else 'n/a'}")
    click.echo(f"  Keys above {flux_threshold:.0%} threshold:")
    click.echo(_format_report(report, threshold=flux_threshold))
    return True
