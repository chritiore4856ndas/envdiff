"""Formatters for displaying diff results in the terminal."""

from dataclasses import dataclass
from typing import Literal

from envdiff.comparator import DiffResult

Format = Literal["text", "json", "table"]


def _color(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def _red(text: str) -> str:
    return _color(text, "31")


def _yellow(text: str) -> str:
    return _color(text, "33")


def _green(text: str) -> str:
    return _color(text, "32")


def format_text(result: DiffResult, color: bool = True) -> str:
    lines: list[str] = []

    for key in sorted(result.only_in_a):
        msg = f"  - {key}  (only in A)"
        lines.append(_red(msg) if color else msg)

    for key in sorted(result.only_in_b):
        msg = f"  + {key}  (only in B)"
        lines.append(_green(msg) if color else msg)

    for key, (val_a, val_b) in sorted(result.mismatched.items()):
        a_display = repr(val_a) if val_a is not None else "<empty>"
        b_display = repr(val_b) if val_b is not None else "<empty>"
        msg = f"  ~ {key}  A={a_display}  B={b_display}"
        lines.append(_yellow(msg) if color else msg)

    if not lines:
        msg = "No differences found."
        return _green(msg) if color else msg

    header = f"Found {len(result.only_in_a)} missing, {len(result.only_in_b)} extra, {len(result.mismatched)} mismatched keys."
    return "\n".join([header, ""] + lines)


def format_json(result: DiffResult) -> str:
    import json

    data = {
        "only_in_a": sorted(result.only_in_a),
        "only_in_b": sorted(result.only_in_b),
        "mismatched": {
            k: {"a": v[0], "b": v[1]}
            for k, v in sorted(result.mismatched.items())
        },
    }
    return json.dumps(data, indent=2)


def format_table(result: DiffResult, color: bool = True) -> str:
    rows: list[tuple[str, str, str, str]] = []

    for key in sorted(result.only_in_a):
        rows.append((key, "MISSING", "<present>", "<absent>"))
    for key in sorted(result.only_in_b):
        rows.append((key, "EXTRA", "<absent>", "<present>"))
    for key, (val_a, val_b) in sorted(result.mismatched.items()):
        rows.append((key, "MISMATCH", str(val_a) if val_a else "", str(val_b) if val_b else ""))

    if not rows:
        msg = "No differences found."
        return _green(msg) if color else msg

    col_widths = [max(len(r[i]) for r in rows + [("KEY", "STATUS", "A", "B")]) for i in range(4)]
    fmt = "  ".join(f"{{:<{w}}}" for w in col_widths)
    header = fmt.format("KEY", "STATUS", "A", "B")
    sep = "  ".join("-" * w for w in col_widths)
    body_lines = [fmt.format(*row) for row in rows]
    return "\n".join([header, sep] + body_lines)
