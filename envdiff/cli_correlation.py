"""CLI integration for correlation analysis."""
from __future__ import annotations
import json
import click
from typing import List
from envdiff.comparator import DiffResult
from envdiff.differ_correlation import correlate_results


def correlation_options(f):
    f = click.option(
        "--correlate",
        is_flag=True,
        default=False,
        help="Show key co-change correlation across multiple diff results.",
    )(f)
    f = click.option(
        "--correlate-top",
        default=10,
        show_default=True,
        metavar="N",
        help="Number of top correlated pairs to display.",
    )(f)
    f = click.option(
        "--correlate-json",
        is_flag=True,
        default=False,
        help="Output correlation report as JSON.",
    )(f)
    return f


def apply_correlation(
    results: List[DiffResult],
    correlate: bool,
    correlate_top: int,
    correlate_json: bool,
) -> bool:
    """Run correlation analysis and print results. Returns True if output was emitted."""
    if not correlate:
        return False

    report = correlate_results(results)

    if correlate_json:
        click.echo(json.dumps(report.as_dict(), indent=2))
        return True

    if not report.pairs:
        click.echo("No co-changing key pairs found.")
        return True

    click.echo(f"Key correlation across {report.total_snapshots} snapshot(s):")
    click.echo(f"  {'KEY A':<24} {'KEY B':<24} {'RATIO':>6}  CO-CHANGES")
    click.echo("  " + "-" * 64)
    for pair in report.strongest(n=correlate_top):
        click.echo(
            f"  {pair.key_a:<24} {pair.key_b:<24} {pair.correlation_ratio:>6.2f}  {pair.co_changes}"
        )
    return True
