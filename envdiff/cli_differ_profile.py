"""CLI integration: --profile flag that runs a saved profile through multi-diff."""
from __future__ import annotations

import sys

import click

from envdiff.differ_profile import ProfileNotFoundError, run_profile_diff
from envdiff.formatter_multi import format_multi_text, format_multi_summary


def profile_diff_options(func):
    """Decorator that attaches --profile and --summary flags to a Click command."""
    func = click.option(
        "--summary",
        is_flag=True,
        default=False,
        help="Show a one-line summary instead of the full diff table.",
    )(func)
    func = click.option(
        "--profile",
        "profile_name",
        default=None,
        help="Name of a saved profile to diff.",
    )(func)
    return func


def apply_profile_diff(profile_name: str | None, summary: bool) -> bool:
    """Run the profile diff and print output.  Returns True when a diff was found."""
    if not profile_name:
        return False

    try:
        pdr = run_profile_diff(profile_name)
    except ProfileNotFoundError as exc:
        click.echo(str(exc), err=True)
        sys.exit(2)
    except ValueError as exc:
        click.echo(str(exc), err=True)
        sys.exit(2)

    if summary:
        click.echo(format_multi_summary(pdr.result))
    else:
        click.echo(format_multi_text(pdr.result))

    return pdr.result.has_diff
