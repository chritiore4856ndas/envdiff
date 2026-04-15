"""Format a :class:`~envdiff.sorter.GroupedDiff` for human or machine consumption."""
from __future__ import annotations

import json
from typing import Optional

from envdiff.sorter import GroupedDiff, total

# ---------------------------------------------------------------------------
# ANSI helpers
# ---------------------------------------------------------------------------

def _color(code: str, text: str, enabled: bool) -> str:
    if not enabled:
        return text
    return f"\033[{code}m{text}\033[0m"


def _red(text: str, enabled: bool = True) -> str:
    return _color("31", text, enabled)


def _yellow(text: str, enabled: bool = True) -> str:
    return _color("33", text, enabled)


def _green(text: str, enabled: bool = True) -> str:
    return _color("32", text, enabled)


# ---------------------------------------------------------------------------
# Text formatter
# ---------------------------------------------------------------------------

def format_text(grouped: GroupedDiff, *, use_color: bool = True) -> str:
    """Render *grouped* as a human-readable text report."""
    lines: list[str] = []

    if total(grouped) == 0:
        lines.append(_green("✔ No differences found.", use_color))
        return "\n".join(lines)

    if grouped.missing_in_b:
        lines.append(_red("Keys only in A (missing in B):", use_color))
        for key, value in sorted(grouped.missing_in_b.items()):
            val_str = repr(value) if value is not None else "(unset)"
            lines.append(f"  {_red('-', use_color)} {key}={val_str}")

    if grouped.missing_in_a:
        lines.append(_yellow("Keys only in B (missing in A):", use_color))
        for key, value in sorted(grouped.missing_in_a.items()):
            val_str = repr(value) if value is not None else "(unset)"
            lines.append(f"  {_yellow('+', use_color)} {key}={val_str}")

    if grouped.mismatched:
        lines.append(_yellow("Mismatched values:", use_color))
        for key, (val_a, val_b) in sorted(grouped.mismatched.items()):
            a_str = repr(val_a) if val_a is not None else "(unset)"
            b_str = repr(val_b) if val_b is not None else "(unset)"
            lines.append(
                f"  {_yellow('~', use_color)} {key}: "
                f"{_red(a_str, use_color)} → {_green(b_str, use_color)}"
            )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# JSON formatter
# ---------------------------------------------------------------------------

def format_json(grouped: GroupedDiff) -> str:
    """Render *grouped* as a JSON string."""
    payload = {
        "missing_in_b": {
            k: v for k, v in grouped.missing_in_b.items()
        },
        "missing_in_a": {
            k: v for k, v in grouped.missing_in_a.items()
        },
        "mismatched": {
            k: {"a": pair[0], "b": pair[1]}
            for k, pair in grouped.mismatched.items()
        },
        "total_differences": total(grouped),
    }
    return json.dumps(payload, indent=2, default=str)
