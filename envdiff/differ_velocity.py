"""Measures how fast keys are changing across a sequence of DiffResults."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from envdiff.comparator import DiffResult


@dataclass
class VelocityEntry:
    key: str
    change_count: int
    total_snapshots: int

    @property
    def rate(self) -> float:
        if self.total_snapshots == 0:
            return 0.0
        return self.change_count / self.total_snapshots

    def __repr__(self) -> str:
        return f"VelocityEntry({self.key!r}, rate={self.rate:.2f})"

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "change_count": self.change_count,
            "total_snapshots": self.total_snapshots,
            "rate": round(self.rate, 4),
        }


@dataclass
class VelocityReport:
    entries: List[VelocityEntry] = field(default_factory=list)

    def fastest(self, n: int = 5) -> List[VelocityEntry]:
        return sorted(self.entries, key=lambda e: e.rate, reverse=True)[:n]

    def as_dict(self) -> dict:
        return {"entries": [e.as_dict() for e in self.entries]}


def velocity_results(results: List[DiffResult]) -> VelocityReport:
    """Count how often each key appears in a diff (missing or mismatched)."""
    counts: dict[str, int] = {}
    total = len(results)

    for result in results:
        seen = set(result.only_in_a) | set(result.only_in_b) | set(result.mismatched)
        for key in seen:
            counts[key] = counts.get(key, 0) + 1

    entries = [
        VelocityEntry(key=k, change_count=v, total_snapshots=total)
        for k, v in sorted(counts.items(), key=lambda x: x[1], reverse=True)
    ]
    return VelocityReport(entries=entries)
