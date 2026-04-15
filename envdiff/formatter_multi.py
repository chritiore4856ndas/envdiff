"""Text and table formatters for MultiDiffResult."""
from __future__ import annotations

from typing import List

from envdiff.differ import MultiDiffResult
from envdiff.formatter import _red, _yellow, _green

_COL_WIDTH = 20


def _cell(value: str | None, reference: str | None) -> str:
    if value is None:
        return _red("<missing>".ljust(_COL_WIDTH))
    if reference is not None and value != reference:
        return _yellow(value.ljust(_COL_WIDTH))
    return _green(value.ljust(_COL_WIDTH))


def format_multi_text(result: MultiDiffResult, *, only_diff: bool = True) -> str:
    """Return a human-readable table of all files side-by-side."""
    if not result.files:
        return "No files to compare.\n"

    keys = result.differing_keys if only_diff else set(result.matrix.keys())
    if not keys:
        return "All files are identical.\n"

    short = [f.split("/")[-1] for f in result.files]
    header = "KEY".ljust(24) + "".join(h.ljust(_COL_WIDTH) for h in short)
    sep = "-" * len(header)

    lines: List[str] = [header, sep]
    for key in sorted(keys):
        vals = result.matrix[key]
        first = vals.get(result.files[0])
        row = key.ljust(24) + "".join(_cell(vals[f], first) for f in result.files)
        lines.append(row)

    return "\n".join(lines) + "\n"


def format_multi_summary(result: MultiDiffResult) -> str:
    """One-line summary per file pair."""
    if not result.pairwise:
        return "Nothing to compare.\n"
    lines = []
    for (a, b), diff in result.pairwise.items():
        na, nb = a.split("/")[-1], b.split("/")[-1]
        total = len(diff.only_in_a) + len(diff.only_in_b) + len(diff.mismatched)
        status = _green("identical") if total == 0 else _red(f"{total} difference(s)")
        lines.append(f"{na} vs {nb}: {status}")
    return "\n".join(lines) + "\n"
