"""CLI integration for differ_signature: --signature flag."""
from __future__ import annotations

import json
from typing import List

import click

from envdiff.comparator import DiffResult
from envdiff.differ_signature import signature_results


def signature_options(f):
    f = click.option(
        "--signature",
        is_flag=True,
        default=False,
        help="Show per-key value signature report across compared envs.",
    )(f)
    f = click.option(
        "--signature-json",
        is_flag=True,
        default=False,
        help="Output signature report as JSON.",
    )(f)
    return f


def apply_signature(
    result: DiffResult,
    signature: bool,
    signature_json: bool,
) -> None:
    """Print signature report if requested. Accepts a single DiffResult."""
    if not signature and not signature_json:
        return

    report = signature_results([result])

    if signature_json:
        click.echo(json.dumps(report.as_dict(), indent=2))
        return

    if not report.entries:
        click.echo("signature: no keys found")
        return

    click.echo(f"{'KEY':<30} {'STABLE':<8} SIGNATURE")
    click.echo("-" * 56)
    for e in report.entries:
        stable_label = "yes" if e.stable else "no"
        click.echo(f"{e.key:<30} {stable_label:<8} {e.signature}")
