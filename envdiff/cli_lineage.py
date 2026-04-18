"""CLI integration for key lineage reporting."""
from __future__ import annotations
import json
import click
from typing import Callable
from envdiff.differ_lineage import build_lineage, LineageReport


def lineage_options(f: Callable) -> Callable:
    f = click.option("--lineage", is_flag=True, default=False, help="Show key lineage report.")(f)
    f = click.option("--lineage-json", is_flag=True, default=False, help="Output lineage as JSON.")(f)
    f = click.option("--lineage-ephemeral", is_flag=True, default=False, help="Show only ephemeral keys.")(f)
    return f


def apply_lineage(
    results,
    lineage: bool,
    lineage_json: bool,
    lineage_ephemeral: bool,
) -> bool:
    """Build and optionally print lineage report. Returns True if lineage was emitted."""
    if not (lineage or lineage_json or lineage_ephemeral):
        return False

    report: LineageReport = build_lineage(results)

    if lineage_json:
        click.echo(json.dumps(report.as_dict(), indent=2))
        return True

    entries = report.ephemeral() if lineage_ephemeral else list(report.entries.values())

    if not entries:
        click.echo("No lineage data.")
        return True

    header = "Ephemeral keys" if lineage_ephemeral else "Key lineage"
    click.echo(f"\n{header} ({len(entries)} keys):")
    click.echo("-" * 48)
    for entry in sorted(entries, key=lambda e: e.key):
        span = f"snapshots {entry.first_seen}-{entry.last_seen}"
        history = ", ".join(entry.status_history)
        click.echo(f"  {entry.key:<30} {span}  [{history}]")

    return True
