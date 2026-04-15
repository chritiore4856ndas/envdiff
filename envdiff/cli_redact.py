"""Click decorator that adds --redact / --redact-pattern options to a command."""
from __future__ import annotations

import functools
from typing import Callable

import click

from envdiff.redactor import redact_diff


def redact_options(func: Callable) -> Callable:  # type: ignore[type-arg]
    """Decorator that injects --redact and --redact-pattern into a Click command."""

    @click.option(
        "--redact",
        is_flag=True,
        default=False,
        help="Redact sensitive values (passwords, tokens, keys, …) from output.",
    )
    @click.option(
        "--redact-pattern",
        "redact_patterns",
        multiple=True,
        metavar="PATTERN",
        help="Additional regex pattern to treat as sensitive (can repeat).",
    )
    @functools.wraps(func)
    def wrapper(*args: object, redact: bool, redact_patterns: tuple[str, ...], **kwargs: object) -> object:
        return func(*args, redact=redact, redact_patterns=redact_patterns, **kwargs)

    return wrapper


def apply_redaction(
    result,  # DiffResult
    redact: bool,
    redact_patterns: tuple[str, ...],
):
    """Apply redaction to *result* if the flag is set; return (possibly modified) result."""
    if not redact and not redact_patterns:
        return result
    return redact_diff(result, extra_patterns=list(redact_patterns))
