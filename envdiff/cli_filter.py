"""Shared Click options for key filtering, reused by cli.py."""

from __future__ import annotations

import functools
from typing import Callable

import click


def filter_options(func: Callable) -> Callable:  # type: ignore[type-arg]
    """Decorator that attaches --exclude and --include options to a Click command."""

    @click.option(
        "--exclude",
        "exclude_patterns",
        multiple=True,
        metavar="PATTERN",
        help="Regex pattern for keys to exclude (repeatable).",
    )
    @click.option(
        "--include",
        "include_patterns",
        multiple=True,
        metavar="PATTERN",
        help="Regex pattern for keys to include (repeatable). When set, all other keys are hidden.",
    )
    @functools.wraps(func)
    def wrapper(*args, **kwargs):  # type: ignore[no-untyped-def]
        return func(*args, **kwargs)

    return wrapper


def apply_filters(
    result,  # DiffResult
    exclude_patterns: tuple[str, ...],
    include_patterns: tuple[str, ...],
):
    """Convenience wrapper that calls filter_diff only when patterns are provided."""
    from envdiff.filter import filter_diff

    if not exclude_patterns and not include_patterns:
        return result

    return filter_diff(
        result,
        exclude_patterns=exclude_patterns,
        include_patterns=include_patterns,
    )
