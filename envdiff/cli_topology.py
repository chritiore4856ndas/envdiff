"""CLI integration for topology analysis."""
from __future__ import annotations

import json
from typing import Dict, List

import click

from envdiff.comparator import DiffResult
from envdiff.differ_topology import TopologyReport, topology_diff


def _format_report(report: TopologyReport, *, verbose: bool = False) -> str:
    lines: List[str] = []
    if not report.entries:
        return "topology: no keys found"
    lines.append(
        f"topology: {len(report.universal_keys)} universal, "
        f"{len(report.fragmented_keys)} fragmented"
    )
    for entry in report.fragmented_keys:
        absent = ", ".join(entry.absent_in)
        lines.append(
            f"  {entry.key}: missing in [{absent}] "
            f"(presence {entry.presence_rate:.0%})"
        )
    if verbose:
        for entry in report.universal_keys:
            lines.append(f"  {entry.key}: universal")
    return "\n".join(lines)


def topology_options(f):
    f = click.option(
        "--topology",
        is_flag=True,
        default=False,
        help="Show key topology across all compared envs.",
    )(f)
    f = click.option(
        "--topology-verbose",
        is_flag=True,
        default=False,
        help="Include universal keys in topology output.",
    )(f)
    f = click.option(
        "--topology-json",
        is_flag=True,
        default=False,
        help="Emit topology report as JSON.",
    )(f)
    return f


def apply_topology(
    results: Dict[str, DiffResult],
    *,
    topology: bool,
    topology_verbose: bool,
    topology_json: bool,
) -> bool:
    """Run topology analysis and print results. Returns True if flag was active."""
    if not topology:
        return False

    report = topology_diff(results)

    if topology_json:
        click.echo(json.dumps(report.as_dict(), indent=2))
    else:
        click.echo(_format_report(report, verbose=topology_verbose))

    return True
