"""Stability analysis: measures how stable each key is across multiple diff results."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from envdiff.comparator import DiffResult


@dataclass
class StabilityEntry:
    key: str
    stable_count: int
    total_count: int

    @property
    def stability_rate(self) -> float:
        if self.total_count == 0:
            return 1.0
        return self.stable_count / self.total_count

    @property
    def is_stable(self) -> bool:
        return self.stability_rate >= 0.8

    def __repr__(self) -> str:
        return (
            f"StabilityEntry(key={self.key!r}, "
            f"rate={self.stability_rate:.2f}, stable={self.is_stable})"
        )

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "stable_count": self.stable_count,
            "total_count": self.total_count,
            "stability_rate": round(self.stability_rate, 4),
            "is_stable": self.is_stable,
        }


@dataclass
class StabilityReport:
    entries: List[StabilityEntry] = field(default_factory=list)

    def unstable(self, threshold: float = 0.8) -> List[StabilityEntry]:
        return [e for e in self.entries if e.stability_rate < threshold]

    def stable(self, threshold: float = 0.8) -> List[StabilityEntry]:
        return [e for e in self.entries if e.stability_rate >= threshold]

    def as_dict(self) -> dict:
        return {"entries": [e.as_dict() for e in self.entries]}


def stability_diff(results: List[DiffResult]) -> StabilityReport:
    """Compute per-key stability across a sequence of DiffResult snapshots."""
    if not results:
        return StabilityReport()

    all_keys: set[str] = set()
    for r in results:
        all_keys.update(r.only_in_a)
        all_keys.update(r.only_in_b)
        all_keys.update(r.mismatched.keys())
        all_keys.update(r.matching.keys())

    entries: List[StabilityEntry] = []
    for key in sorted(all_keys):
        stable_count = 0
        total_count = 0
        for r in results:
            if key in r.only_in_a or key in r.only_in_b or key in r.mismatched:
                total_count += 1
            elif key in r.matching:
                stable_count += 1
                total_count += 1
        entries.append(StabilityEntry(key=key, stable_count=stable_count, total_count=total_count))

    return StabilityReport(entries=entries)
