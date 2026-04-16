"""Click decorators to wire ignore-file support into the main CLI."""
from __future__ import annotations

import functools
from pathlib import Path

import click

from envdiff.ignorer import load_ignore_patterns, apply_ignore, DEFAULT_IGNORE_FILE


def ignore_options(fn):
    @click.option(
        "--ignore-file",
        default=None,
        metavar="PATH",
        help=f"Path to ignore file (default: {DEFAULT_IGNORE_FILE} if present).",
    )
    @click.option(
        "--ignore",
        multiple=True,
        metavar="PATTERN",
        help="Glob pattern for keys to ignore (repeatable).",
    )
    @functools.wraps(fn)
    def wrapper(*args, ignore_file, ignore, **kwargs):
        return fn(*args, _ignore_file=ignore_file, _ignore_patterns=ignore, **kwargs)

    return wrapper


def apply_ignore_options(result, ignore_file, ignore_patterns):
    """Collect patterns from file + CLI flags and apply them to *result*."""
    patterns: list[str] = list(ignore_patterns or [])

    # fall back to default ignore file when no explicit path given
    candidate = Path(ignore_file) if ignore_file else Path(DEFAULT_IGNORE_FILE)
    patterns.extend(load_ignore_patterns(candidate))

    return apply_ignore(result, patterns)
