"""Summarizer: produce a concise statistics summary from a GroupedDiff."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from envdiff.sorter import GroupedDiff, total


@dataclass
class DiffSummary:
    missing_in_b: int
    missing_in_a: int
    mismatched: int
    total_keys: int
    clean: bool

    def as_dict(self) -> dict:
        return {
            "missing_in_b": self.missing_in_b,
            "missing_in_a": self.missing_in_a,
            "mismatched": self.mismatched,
            "total_keys": self.total_keys,
            "clean": self.clean,
        }


def summarize(grouped: GroupedDiff) -> DiffSummary:
    """Return a DiffSummary for *grouped*."""
    missing_in_b = len(grouped.missing_in_b)
    missing_in_a = len(grouped.missing_in_a)
    mismatched = len(grouped.mismatched)
    total_keys = total(grouped)
    clean = total_keys == 0
    return DiffSummary(
        missing_in_b=missing_in_b,
        missing_in_a=missing_in_a,
        mismatched=mismatched,
        total_keys=total_keys,
        clean=clean,
    )


def format_summary(summary: DiffSummary, label_a: str = "A", label_b: str = "B") -> str:
    """Return a human-readable one-block summary string."""
    if summary.clean:
        return "No differences found."

    lines = ["Diff summary:"]
    if summary.missing_in_b:
        lines.append(
            f"  {summary.missing_in_b} key(s) only in {label_a} (missing in {label_b})"
        )
    if summary.missing_in_a:
        lines.append(
            f"  {summary.missing_in_a} key(s) only in {label_b} (missing in {label_a})"
        )
    if summary.mismatched:
        lines.append(f"  {summary.mismatched} key(s) with mismatched values")
    lines.append(f"  {summary.total_keys} total differing key(s)")
    return "\n".join(lines)
