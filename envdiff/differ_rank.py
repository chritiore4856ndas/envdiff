"""Rank keys by how frequently they differ across multiple diff results."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import List

from envdiff.comparator import DiffResult


@dataclass
class RankedKey:
    key: str
    count: int

    def __repr__(self) -> str:  # pragma: no cover
        return f"RankedKey({self.key!r}, count={self.count})"


@dataclass
class RankReport:
    ranked: List[RankedKey] = field(default_factory=list)

    @property
    def top(self) -> RankedKey | None:
        return self.ranked[0] if self.ranked else None

    def as_dict(self) -> list[dict]:
        return [{"key": r.key, "count": r.count} for r in self.ranked]


def rank_diffs(results: list[DiffResult]) -> RankReport:
    """Count how many results each key appears in as a diff (missing or mismatched)."""
    counter: Counter = Counter()
    for result in results:
        problematic = set(result.only_in_a) | set(result.only_in_b) | set(result.mismatched)
        for key in problematic:
            counter[key] += 1
    ranked = [RankedKey(key=k, count=c) for k, c in counter.most_common()]
    return RankReport(ranked=ranked)


def format_rank(report: RankReport) -> str:
    if not report.ranked:
        return "No differing keys found."
    lines = ["Key Rank (most problematic first):", ""]
    for i, entry in enumerate(report.ranked, 1):
        lines.append(f"  {i:>3}. {entry.key} — {entry.count} occurrence(s)")
    return "\n".join(lines)
