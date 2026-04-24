"""CLI integration for density analysis."""
from __future__ import annotations

import json
from typing import List, Tuple

import click

from envdiff.comparator import DiffResult
from envdiff.differ_density import DensityReport, density_results


def _format_report(report: DensityReport, threshold: float) -> str:
    if not report.entries:
        return "(no density data)"
    lines = ["Density Report:", "-" * 36]
    for e in report.entries:
        flag = "" if e.is_dense(threshold) else "  [SPARSE]"
        lines.append(
            f"  {e.env_name:<20} {e.present:>3}/{e.total:<3}  "
            f"({e.density_rate():.0%}){flag}"
        )
    sparse = report.sparse(threshold)
    if sparse:
        lines.append(f"\n{len(sparse)} sparse environment(s) below {threshold:.0%} threshold.")
    else:
        lines.append("\nAll environments meet the density threshold.")
    return "\n".join(lines)


def density_options(f):
    f = click.option(
        "--density",
        is_flag=True,
        default=False,
        help="Show key-density report across all compared environments.",
    )(f)
    f = click.option(
        "--density-threshold",
        default=0.8,
        show_default=True,
        type=float,
        help="Fraction of keys an env must have to be considered dense.",
    )(f)
    f = click.option(
        "--density-json",
        is_flag=True,
        default=False,
        help="Emit density report as JSON instead of text.",
    )(f)
    return f


def apply_density(
    results: List[DiffResult],
    names: List[str],
    density: bool,
    density_threshold: float,
    density_json: bool,
) -> bool:
    """Print density report if --density flag is set. Returns True if activated."""
    if not density:
        return False
    report = density_results(results, names=names)
    if density_json:
        click.echo(json.dumps(report.as_dict(), indent=2))
    else:
        click.echo(_format_report(report, density_threshold))
    return True
