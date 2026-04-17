"""CLI integration for snapshot diffing."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

import click

from envdiff.differ_snapshot import diff_against_snapshot, save_snapshot


def snapshot_options(cmd: Callable) -> Callable:
    cmd = click.option(
        "--snapshot-save",
        "snapshot_save",
        default=None,
        metavar="NAME",
        help="Save current env files as a named snapshot.",
    )(cmd)
    cmd = click.option(
        "--snapshot-diff",
        "snapshot_diff",
        default=None,
        metavar="NAME",
        help="Diff current env files against a saved snapshot.",
    )(cmd)
    cmd = click.option(
        "--snapshot-store",
        "snapshot_store",
        default=".envdiff_snapshots",
        show_default=True,
        metavar="DIR",
        help="Directory where snapshots are stored.",
    )(cmd)
    return cmd


def apply_snapshot(
    ctx: click.Context,
    file_a: str,
    file_b: str,
    snapshot_save: str | None,
    snapshot_diff: str | None,
    snapshot_store: str,
) -> bool:
    """Return True if snapshot handling consumed the output (caller should stop)."""
    store = Path(snapshot_store)
    files = [f for f in [file_a, file_b] if f]

    if snapshot_save:
        dest = save_snapshot(store, snapshot_save, files)
        click.echo(f"Snapshot '{snapshot_save}' saved to {dest}")
        return True

    if snapshot_diff:
        report = diff_against_snapshot(store, snapshot_diff, files)
        click.echo(json.dumps(report.as_dict(), indent=2))
        if not report.is_clean():
            ctx.exit(1)
        return True

    return False
