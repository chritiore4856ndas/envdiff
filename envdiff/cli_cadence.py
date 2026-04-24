"""CLI integration for cadence analysis (--cadence flag)."""
from __future__ import annotations

import json
from typing import List

import click

from envdiff.comparator import DiffResult
from envdiff.differ_cadence import CadenceReport, cadence_diff


def _format_report(report: CadenceReport, *, show_stable: bool = False) -> str:
    lines: List[str] = []
    entries = report.entries if show_stable else [
        e for e in report.entries if e.change_count > 0
    ]
    if not entries:
        return "cadence: all keys are stable across snapshots"
    lines.append(f"cadence report ({len(report.regular())} regular, "
                 f"{len(report.irregular())} irregular):")
    for entry in sorted(entries, key=lambda e: -e.cadence_rate):
        tag = "regular" if entry.is_regular else "irregular"
        lines.append(
            f"  {entry.key:40s}  rate={entry.cadence_rate:.2f}  [{tag}]"
        )
    return "\n".join(lines)


def cadence_options(f):
    f = click.option(
        "--cadence",
        is_flag=True,
        default=False,
        help="Show cadence (change regularity) analysis across multiple results.",
    )(f)
    f = click.option(
        "--cadence-json",
        is_flag=True,
        default=False,
        help="Emit cadence report as JSON instead of text.",
    )(f)
    f = click.option(
        "--cadence-show-stable",
        is_flag=True,
        default=False,
        help="Include stable (never-changing) keys in the cadence output.",
    )(f)
    return f


def apply_cadence(
    results: List[DiffResult],
    *,
    cadence: bool,
    cadence_json: bool,
    cadence_show_stable: bool,
) -> bool:
    """Run cadence analysis and print results.  Returns True if flag was active."""
    if not cadence:
        return False

    report = cadence_diff(results)

    if cadence_json:
        click.echo(json.dumps(report.as_dict(), indent=2))
    else:
        click.echo(_format_report(report, show_stable=cadence_show_stable))

    return True
