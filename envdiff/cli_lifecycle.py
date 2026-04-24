"""CLI integration for the lifecycle analysis feature."""
from __future__ import annotations

import functools
from typing import Callable

import click

from envdiff.differ_lifecycle import lifecycle_diff, LifecycleReport


def _format_report(report: LifecycleReport, verbose: bool) -> str:
    if not report.entries:
        return ""
    lines = ["\n=== Key Lifecycle ==="]
    for e in report.entries:
        if not verbose and e.stage == "stable":
            continue
        marker = {
            "new": "[+]",
            "removed": "[-]",
            "degrading": "[!]",
            "recovered": "[~]",
            "stable": "[ ]",
        }.get(e.stage, "[?]")
        lines.append(f"  {marker} {e.key:<30} {e.stage}  (issues: {e.issue_count})")
    return "\n".join(lines) if len(lines) > 1 else ""


def lifecycle_options(cmd: Callable) -> Callable:
    @click.option(
        "--lifecycle",
        is_flag=True,
        default=False,
        help="Show key lifecycle analysis across multiple diff results.",
    )
    @click.option(
        "--lifecycle-verbose",
        is_flag=True,
        default=False,
        help="Include stable keys in lifecycle output.",
    )
    @functools.wraps(cmd)
    def wrapper(*args, lifecycle: bool, lifecycle_verbose: bool, **kwargs):
        return cmd(*args, lifecycle=lifecycle, lifecycle_verbose=lifecycle_verbose, **kwargs)

    return wrapper


def apply_lifecycle(
    results: list,
    lifecycle: bool,
    lifecycle_verbose: bool,
) -> bool:
    """Print lifecycle report if --lifecycle is set. Returns True if printed."""
    if not lifecycle:
        return False
    report = lifecycle_diff(results)
    output = _format_report(report, verbose=lifecycle_verbose)
    if output:
        click.echo(output)
    return True
