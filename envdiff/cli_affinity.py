"""CLI integration for affinity analysis."""
from __future__ import annotations

import json
from typing import Callable, List

import click

from envdiff.differ_affinity import affinity_diff


def affinity_options(func: Callable) -> Callable:
    func = click.option(
        "--affinity",
        is_flag=True,
        default=False,
        help="Show key affinity analysis across multiple diff results.",
    )(func)
    func = click.option(
        "--affinity-threshold",
        default=0.8,
        show_default=True,
        type=float,
        help="Minimum affinity ratio to highlight a pair as strongly related.",
    )(func)
    func = click.option(
        "--affinity-json",
        is_flag=True,
        default=False,
        help="Output affinity report as JSON.",
    )(func)
    return func


def apply_affinity(
    results,
    *,
    affinity: bool,
    affinity_threshold: float,
    affinity_json: bool,
) -> bool:
    """Run affinity analysis and print results. Returns True if output was produced."""
    if not affinity:
        return False

    report = affinity_diff(results)

    if affinity_json:
        click.echo(json.dumps(report.as_dict(), indent=2))
        return True

    if not report.pairs:
        click.echo("affinity: no co-occurring problematic keys found.")
        return True

    strong = report.strong(threshold=affinity_threshold)
    click.echo(f"affinity: {len(report.pairs)} pair(s) across {report.total_snapshots} snapshot(s)")

    if strong:
        click.echo(f"  strongly related (>= {affinity_threshold:.0%}):")
        for p in strong:
            click.echo(f"    {p.key_a} <-> {p.key_b}  ({p.affinity_ratio():.0%})")
    else:
        click.echo(f"  no pairs above threshold {affinity_threshold:.0%}")

    click.echo("  all pairs:")
    for p in report.pairs:
        click.echo(f"    {p.key_a} <-> {p.key_b}  co={p.co_occurrences}/{p.total} ({p.affinity_ratio():.0%})")

    return True
