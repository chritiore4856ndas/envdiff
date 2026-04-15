"""Aggregate formatting and exit-code logic into a single report call."""
from __future__ import annotations

import sys
from typing import TextIO

from envdiff.comparator import DiffResult, has_diff
from envdiff.formatter import format_json, format_text
from envdiff.sorter import GroupedDiff, group_diff

_FORMATS = ("text", "json")


def build_report(
    result: DiffResult,
    fmt: str = "text",
    use_color: bool = True,
) -> str:
    """Return a formatted report string for *result*.

    Parameters
    ----------
    result:
        Raw diff produced by :func:`envdiff.comparator.compare`.
    fmt:
        Output format – ``"text"`` or ``"json"``.
    use_color:
        When *True* ANSI escape codes are included (text format only).

    Raises
    ------
    ValueError
        If *fmt* is not one of the supported format strings.
    """
    if fmt not in _FORMATS:
        raise ValueError(f"Unknown format {fmt!r}. Choose from {_FORMATS}.")

    grouped: GroupedDiff = group_diff(result)

    if fmt == "json":
        return format_json(grouped)
    return format_text(grouped, use_color=use_color)


def emit_report(
    result: DiffResult,
    *,
    fmt: str = "text",
    use_color: bool = True,
    exit_on_diff: bool = False,
    stream: TextIO | None = None,
) -> int:
    """Write the report to *stream* (default: stdout) and return an exit code.

    Returns ``1`` when *exit_on_diff* is ``True`` and differences were found,
    otherwise returns ``0``.
    """
    out = stream or sys.stdout
    out.write(build_report(result, fmt=fmt, use_color=use_color))
    out.write("\n")

    if exit_on_diff and has_diff(result):
        return 1
    return 0
