"""Click options and helpers for baseline management in the CLI."""
from __future__ import annotations

import sys
import click

from envdiff.baseline import save_baseline, load_baseline, diff_against_baseline
from envdiff.comparator import DiffResult, has_diff


def baseline_options(f):
    """Decorator that attaches baseline-related Click options to a command."""
    f = click.option(
        "--save-baseline",
        "save_baseline_path",
        default=None,
        metavar="FILE",
        help="Save the current diff as a baseline to FILE.",
    )(f)
    f = click.option(
        "--baseline",
        "baseline_path",
        default=None,
        metavar="FILE",
        help="Compare diff against a saved baseline; show only new differences.",
    )(f)
    return f


def apply_baseline(
    result: DiffResult,
    baseline_path: str | None,
    save_baseline_path: str | None,
) -> DiffResult:
    """Handle baseline load/save logic and return the (possibly filtered) result.

    Side-effects:
    - Writes a baseline file when *save_baseline_path* is set.
    - Prints a status message to stderr.
    """
    if save_baseline_path:
        dest = save_baseline(result, save_baseline_path)
        click.echo(f"Baseline saved to {dest}", err=True)

    if baseline_path:
        try:
            base = load_baseline(baseline_path)
        except FileNotFoundError as exc:
            click.echo(str(exc), err=True)
            sys.exit(2)
        result = diff_against_baseline(result, base)
        if not has_diff(result):
            click.echo("No new differences compared to baseline.", err=True)

    return result
