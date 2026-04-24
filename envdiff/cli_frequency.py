"""CLI integration for frequency analysis."""
from __future__ import annotations

from typing import Any, List

import click

from envdiff.differ_frequency import FrequencyReport, frequency_diff


def _format_report(report: FrequencyReport, threshold: float, show_rare: bool) -> str:
    if not report.entries:
        return "frequency: no data"

    lines = []
    target = report.rare(threshold) if show_rare else report.common(threshold)
    label = "rare" if show_rare else "common"

    if not target:
        return f"frequency: no {label} keys (threshold={threshold})"

    lines.append(f"frequency ({label}, threshold={threshold}):")
    for entry in target:
        lines.append(
            f"  {entry.key}: {entry.appearances}/{entry.total} "
            f"({entry.frequency_rate:.0%})"
        )
    return "\n".join(lines)


def frequency_options(f: Any) -> Any:
    f = click.option(
        "--frequency",
        is_flag=True,
        default=False,
        help="Show key frequency across multiple diff results.",
    )(f)
    f = click.option(
        "--freq-threshold",
        default=0.5,
        show_default=True,
        type=float,
        help="Frequency threshold (0.0-1.0).",
    )(f)
    f = click.option(
        "--freq-rare",
        is_flag=True,
        default=False,
        help="Show rare keys instead of common keys.",
    )(f)
    return f


def apply_frequency(
    results: List[Any],
    frequency: bool,
    freq_threshold: float,
    freq_rare: bool,
) -> bool:
    if not frequency:
        return False
    report = frequency_diff(results)
    click.echo(_format_report(report, freq_threshold, freq_rare))
    return True
