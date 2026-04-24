"""CLI integration for saturation analysis."""
from __future__ import annotations

from typing import List, Tuple

import click

from envdiff.differ_saturation import SaturationReport, saturation_diff


def _format_report(report: SaturationReport, threshold: float) -> str:
    if not report.entries:
        return "No saturation data available."
    lines = ["Saturation Report:", ""]
    for entry in report.least_saturated():
        bar = "#" * int(entry.saturation_rate * 20)
        flag = " [LOW]" if entry.saturation_rate < threshold else ""
        lines.append(
            f"  {entry.env_name:<20} {bar:<20} {entry.saturation_rate:.0%}"
            f" ({entry.present}/{entry.total}){flag}"
        )
    return "\n".join(lines)


def saturation_options(f):
    f = click.option(
        "--saturation",
        is_flag=True,
        default=False,
        help="Show per-env saturation analysis.",
    )(f)
    f = click.option(
        "--saturation-threshold",
        default=0.8,
        show_default=True,
        type=float,
        help="Rate below which an env is flagged as low saturation.",
    )(f)
    return f


def apply_saturation(
    ctx_results,
    env_names: List[str],
    saturation: bool,
    saturation_threshold: float,
) -> bool:
    """Run saturation analysis and print results. Returns True if flag was active."""
    if not saturation:
        return False
    report = saturation_diff(ctx_results, env_names=env_names)
    click.echo(_format_report(report, threshold=saturation_threshold))
    return True
