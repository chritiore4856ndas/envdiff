"""Prevalence analysis: how often each key appears across multiple diff results."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence

from envdiff.comparator import DiffResult


@dataclass
class PrevalenceEntry:
    key: str
    appearances: int
    total: int

    @property
    def prevalence_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return self.appearances / self.total

    @property
    def is_prevalent(self) -> bool:
        return self.prevalence_rate >= 0.5

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"PrevalenceEntry(key={self.key!r}, "
            f"appearances={self.appearances}, total={self.total}, "
            f"rate={self.prevalence_rate:.2f})"
        )

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "appearances": self.appearances,
            "total": self.total,
            "prevalence_rate": round(self.prevalence_rate, 4),
            "is_prevalent": self.is_prevalent,
        }


@dataclass
class PrevalenceReport:
    entries: List[PrevalenceEntry] = field(default_factory=list)

    def prevalent(self) -> List[PrevalenceEntry]:
        return [e for e in self.entries if e.is_prevalent]

    def rare(self) -> List[PrevalenceEntry]:
        return [e for e in self.entries if not e.is_prevalent]

    def as_dict(self) -> dict:
        return {"entries": [e.as_dict() for e in self.entries]}


def prevalence_diff(results: Sequence[DiffResult]) -> PrevalenceReport:
    """Count how many results each key appears in (as a differing key)."""
    if not results:
        return PrevalenceReport()

    total = len(results)
    counts: dict[str, int] = {}

    for result in results:
        seen = set(result.only_in_a) | set(result.only_in_b) | set(result.mismatched)
        for key in seen:
            counts[key] = counts.get(key, 0) + 1

    entries = [
        PrevalenceEntry(key=k, appearances=v, total=total)
        for k, v in sorted(counts.items(), key=lambda x: -x[1])
    ]
    return PrevalenceReport(entries=entries)
