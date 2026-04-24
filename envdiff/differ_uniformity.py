"""Uniformity analysis: measures how consistently each key appears across all envs."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence

from envdiff.comparator import DiffResult


@dataclass
class UniformityEntry:
    key: str
    appearances: int
    total: int

    def uniformity_rate(self) -> float:
        if self.total == 0:
            return 1.0
        return self.appearances / self.total

    def is_uniform(self, threshold: float = 0.8) -> bool:
        return self.uniformity_rate() >= threshold

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"UniformityEntry(key={self.key!r}, "
            f"appearances={self.appearances}/{self.total}, "
            f"rate={self.uniformity_rate():.2f})"
        )

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "appearances": self.appearances,
            "total": self.total,
            "uniformity_rate": round(self.uniformity_rate(), 4),
            "is_uniform": self.is_uniform(),
        }


@dataclass
class UniformityReport:
    entries: List[UniformityEntry] = field(default_factory=list)

    def non_uniform(self, threshold: float = 0.8) -> List[UniformityEntry]:
        return [e for e in self.entries if not e.is_uniform(threshold)]

    def as_dict(self) -> dict:
        return {"entries": [e.as_dict() for e in self.entries]}


def uniformity_diff(
    results: Sequence[DiffResult],
    threshold: float = 0.8,
) -> UniformityReport:
    if not results:
        return UniformityReport()

    total = len(results)
    all_keys: set[str] = set()
    for r in results:
        all_keys.update(r.only_in_a)
        all_keys.update(r.only_in_b)
        all_keys.update(r.mismatched)
        all_keys.update(r.matching)

    entries: List[UniformityEntry] = []
    for key in sorted(all_keys):
        appearances = sum(
            1 for r in results if key in r.matching or key in r.mismatched
        )
        entries.append(UniformityEntry(key=key, appearances=appearances, total=total))

    entries.sort(key=lambda e: e.uniformity_rate())
    return UniformityReport(entries=entries)
