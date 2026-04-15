"""Compute a numeric similarity score between two .env files."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from envdiff.comparator import DiffResult
from envdiff.sorter import GroupedDiff, group_diff


@dataclass
class DiffScore:
    """Numeric summary of how similar two env files are."""

    total_keys: int
    matching: int
    missing_in_b: int
    missing_in_a: int
    mismatched: int

    @property
    def similarity(self) -> float:
        """Return a 0.0–1.0 similarity ratio."""
        if self.total_keys == 0:
            return 1.0
        return round(self.matching / self.total_keys, 4)

    @property
    def grade(self) -> str:
        """Letter grade based on similarity."""
        s = self.similarity
        if s >= 0.95:
            return "A"
        if s >= 0.80:
            return "B"
        if s >= 0.60:
            return "C"
        if s >= 0.40:
            return "D"
        return "F"


def score_diff(result: DiffResult) -> DiffScore:
    """Derive a DiffScore from a DiffResult."""
    grouped: GroupedDiff = group_diff(result)

    missing_in_b = len(grouped.only_in_a)
    missing_in_a = len(grouped.only_in_b)
    mismatched = len(grouped.mismatched)

    all_keys = (
        set(result.only_in_a)
        | set(result.only_in_b)
        | set(result.mismatched)
        | set(result.matching)
    )
    total_keys = len(all_keys)
    matching = len(result.matching)

    return DiffScore(
        total_keys=total_keys,
        matching=matching,
        missing_in_b=missing_in_b,
        missing_in_a=missing_in_a,
        mismatched=mismatched,
    )


def format_score(score: DiffScore) -> str:
    """Return a human-readable score summary."""
    pct = f"{score.similarity * 100:.1f}%"
    lines = [
        f"Similarity : {pct} (grade {score.grade})",
        f"Total keys : {score.total_keys}",
        f"Matching   : {score.matching}",
        f"Mismatched : {score.mismatched}",
        f"Only in A  : {score.missing_in_b}",
        f"Only in B  : {score.missing_in_a}",
    ]
    return "\n".join(lines)
