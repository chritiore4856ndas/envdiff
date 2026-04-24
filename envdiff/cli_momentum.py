"""CLI integration for momentum analysis."""
from __future__ import annotations

from typing import Sequence

import click

from envdiff.comparator import DiffResult
from envdiff.differ_momentum import MomentumReport, momentum_diff


def _format_report(report: MomentumReport, top: int = 10) -> str:
    if not report.entries:
        return "momentum: no data"

    lines = ["=== Momentum Report ==="]
    shown = report.entries[:top]
    for e in shown:
        direction = (
            "↑ accelerating" if e.acceleration > 0.001
            else "↓ decelerating" if e.acceleration < -0.001
            else "→ stable"
        )
        lines.append(
            f"  {e.key:<30} accel={e.acceleration:+.3f}  {direction}"
        )
    lines.append(
        f"\naccelerating={len(report.accelerating())}  "
        f"decelerating={len(report.decelerating())}  "
        f"total={len(report.entries)}"
    )
    return "\n".join(lines)


def momentum_options(f):
    f = click.option(
        "--momentum",
        is_flag=True,
        default=False,
        help="Show momentum (change-rate acceleration) across results.",
    )(f)
    f = click.option(
        "--momentum-window",
        default=2,
        show_default=True,
        type=int,
        help="Window size for grouping results when computing momentum.",
    )(f)
    f = click.option(
        "--momentum-top",
        default=10,
        show_default=True,
        type=int,
        help="Number of top entries to display.",
    )(f)
    return f


def apply_momentum(
    results: Sequence[DiffResult],
    momentum: bool,
    momentum_window: int,
    momentum_top: int,
) -> bool:
    """Run momentum analysis and print results.  Returns True if flag was active."""
    if not momentum:
        return False
    report = momentum_diff(results, window=momentum_window)
    click.echo(_format_report(report, top=momentum_top))
    return True
