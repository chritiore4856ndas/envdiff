"""Heatmap: count how often each key appears as a diff across multiple comparisons."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.comparator import DiffResult


@dataclass
class HeatmapEntry:
    key: str
    count: int

    def __repr__(self) -> str:  # pragma: no cover
        return f"HeatmapEntry(key={self.key!r}, count={self.count})"


@dataclass
class HeatmapReport:
    entries: List[HeatmapEntry] = field(default_factory=list)

    def top(self, n: int = 10) -> List[HeatmapEntry]:
        return self.entries[:n]

    def as_dict(self) -> Dict[str, int]:
        return {e.key: e.count for e in self.entries}


def build_heatmap(results: List[DiffResult]) -> HeatmapReport:
    """Count diff occurrences per key across all DiffResult objects."""
    counts: Dict[str, int] = {}

    for result in results:
        differing_keys = (
            set(result.only_in_a)
            | set(result.only_in_b)
            | set(result.mismatched)
        )
        for key in differing_keys:
            counts[key] = counts.get(key, 0) + 1

    entries = sorted(
        [HeatmapEntry(key=k, count=v) for k, v in counts.items()],
        key=lambda e: e.count,
        reverse=True,
    )
    return HeatmapReport(entries=entries)
