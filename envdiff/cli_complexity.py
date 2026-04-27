"""CLI integration for complexity analysis."""
from __future__ import annotations

from typing import List, Optional

import click

from envdiff.comparator import DiffResult
from envdiff.differ_complexity import ComplexityReport, complexity_diff


def _format_report(report: ComplexityReport, threshold: float = 0.4) -> str:
    if not report.entries:
        return "complexity: no data"
    lines = ["complexity analysis:"]
    for entry in report.entries:
        flag = " [COMPLEX]" if entry.is_complex(threshold) else ""
        lines.append(
            f"  {entry.env_label}: score={entry.complexity_score:.2f}"
            f" ({entry.issues}/{entry.total_keys} issues){flag}"
        )
    avg = report.average_score()
    lines.append(f"  average score: {avg:.2f}")
    mc = report.most_complex()
    if mc:
        lines.append(f"  most complex: {mc.env_label}")
    return "\n".join(lines)


def complexity_options(func):
    func = click.option(
        "--complexity",
        is_flag=True,
        default=False,
        help="Show complexity analysis across compared envs.",
    )(func)
    func = click.option(
        "--complexity-threshold",
        type=float,
        default=0.4,
        show_default=True,
        help="Score threshold above which an env is considered complex.",
    )(func)
    return func


def apply_complexity(
    results: List[DiffResult],
    labels: Optional[List[str]],
    *,
    complexity: bool,
    complexity_threshold: float = 0.4,
) -> bool:
    """Print complexity report if flag is set. Returns True if printed."""
    if not complexity:
        return False
    report = complexity_diff(results, labels=labels)
    click.echo(_format_report(report, threshold=complexity_threshold))
    return True
