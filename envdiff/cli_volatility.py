"""CLI integration for volatility analysis."""
from __future__ import annotations

import json
from typing import List, Tuple, Any

import click

from envdiff.comparator import DiffResult
from envdiff.differ_volatility import VolatilityReport, volatility_diff


def _format_report(report: VolatilityReport, *, top: int = 0) -> str:
    entries = report.entries
    if top:
        entries = sorted(entries, key=lambda e: e.volatility_rate, reverse=True)[:top]
    if not entries:
        return "volatility: no keys tracked"
    lines = ["Volatility Report:", f"  volatile keys : {len(report.volatile())}",
             f"  stable keys   : {len(report.stable())}"]
    lines.append("  " + "-" * 38)
    for e in entries:
        flag = " [VOLATILE]" if e.is_volatile else ""
        lines.append(
            f"  {e.key:<30} rate={e.volatility_rate:.2f}  "
            f"changes={e.change_count}/{e.snapshot_count}{flag}"
        )
    return "\n".join(lines)


def volatility_options(f):
    f = click.option(
        "--volatility", is_flag=True, default=False,
        help="Show per-key volatility across results.",
    )(f)
    f = click.option(
        "--volatility-top", default=0, metavar="N",
        help="Show only the top N most volatile keys.",
    )(f)
    f = click.option(
        "--volatility-json", is_flag=True, default=False,
        help="Emit volatility report as JSON.",
    )(f)
    return f


def apply_volatility(
    results: List[DiffResult],
    *,
    volatility: bool,
    volatility_top: int,
    volatility_json: bool,
) -> bool:
    """Compute and print volatility report.  Returns True if report was printed."""
    if not volatility:
        return False

    report = volatility_diff(results)

    if volatility_json:
        click.echo(json.dumps(report.as_dict(), indent=2))
    else:
        click.echo(_format_report(report, top=volatility_top))

    return True
