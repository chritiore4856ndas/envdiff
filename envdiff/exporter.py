"""Export diff results to various file formats (JSON, CSV, Markdown)."""
from __future__ import annotations

import csv
import io
import json
from typing import Literal

from envdiff.sorter import GroupedDiff

ExportFormat = Literal["json", "csv", "markdown"]


def export_json(grouped: GroupedDiff) -> str:
    """Serialise a GroupedDiff to a JSON string."""
    payload = {
        "missing_in_b": list(grouped.missing_in_b),
        "missing_in_a": list(grouped.missing_in_a),
        "mismatched": [
            {"key": k, "value_a": a, "value_b": b}
            for k, (a, b) in grouped.mismatched.items()
        ],
    }
    return json.dumps(payload, indent=2)


def export_csv(grouped: GroupedDiff) -> str:
    """Serialise a GroupedDiff to a CSV string."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["key", "status", "value_a", "value_b"])
    for key in sorted(grouped.missing_in_b):
        writer.writerow([key, "missing_in_b", "", ""])
    for key in sorted(grouped.missing_in_a):
        writer.writerow([key, "missing_in_a", "", ""])
    for key, (a, b) in sorted(grouped.mismatched.items()):
        writer.writerow([key, "mismatched", a or "", b or ""])
    return buf.getvalue()


def export_markdown(grouped: GroupedDiff) -> str:
    """Serialise a GroupedDiff to a Markdown table string."""
    lines: list[str] = []
    lines.append("| Key | Status | Value A | Value B |")
    lines.append("|-----|--------|---------|---------|")
    for key in sorted(grouped.missing_in_b):
        lines.append(f"| `{key}` | missing in B | | |")
    for key in sorted(grouped.missing_in_a):
        lines.append(f"| `{key}` | missing in A | | |")
    for key, (a, b) in sorted(grouped.mismatched.items()):
        lines.append(f"| `{key}` | mismatched | {a or ''} | {b or ''} |")
    return "\n".join(lines) + "\n"


def export_diff(grouped: GroupedDiff, fmt: ExportFormat) -> str:
    """Dispatch to the correct exporter based on *fmt*."""
    if fmt == "json":
        return export_json(grouped)
    if fmt == "csv":
        return export_csv(grouped)
    if fmt == "markdown":
        return export_markdown(grouped)
    raise ValueError(f"Unknown export format: {fmt!r}")
