"""Resilience analysis: measures how consistently a key survives across diff results."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from envdiff.comparator import DiffResult


@dataclass
class ResilienceEntry:
    key: str
    appearances: int
    total: int
    issue_count: int

    def resilience_rate(self) -> float:
        if self.total == 0:
            return 1.0
        return max(0.0, (self.appearances - self.issue_count) / self.total)

    def is_resilient(self, threshold: float = 0.8) -> bool:
        return self.resilience_rate() >= threshold

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"ResilienceEntry(key={self.key!r}, rate={self.resilience_rate():.2f}, "
            f"appearances={self.appearances}, issues={self.issue_count})"
        )

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "appearances": self.appearances,
            "total": self.total,
            "issue_count": self.issue_count,
            "resilience_rate": round(self.resilience_rate(), 4),
            "is_resilient": self.is_resilient(),
        }


@dataclass
class ResilienceReport:
    entries: List[ResilienceEntry] = field(default_factory=list)

    def fragile(self, threshold: float = 0.8) -> List[ResilienceEntry]:
        return [e for e in self.entries if not e.is_resilient(threshold)]

    def most_resilient(self) -> Optional[ResilienceEntry]:
        return max(self.entries, key=lambda e: e.resilience_rate(), default=None)

    def least_resilient(self) -> Optional[ResilienceEntry]:
        return min(self.entries, key=lambda e: e.resilience_rate(), default=None)

    def as_dict(self) -> dict:
        return {"entries": [e.as_dict() for e in self.entries]}


def resilience_diff(results: List[DiffResult]) -> ResilienceReport:
    if not results:
        return ResilienceReport()

    total = len(results)
    appearances: dict[str, int] = {}
    issues: dict[str, int] = {}

    for r in results:
        all_keys = set(r.only_in_a) | set(r.only_in_b) | set(r.mismatched) | set(r.matching)
        for key in all_keys:
            appearances[key] = appearances.get(key, 0) + 1
        for key in set(r.only_in_a) | set(r.only_in_b) | set(r.mismatched):
            issues[key] = issues.get(key, 0) + 1

    entries = [
        ResilienceEntry(
            key=key,
            appearances=appearances[key],
            total=total,
            issue_count=issues.get(key, 0),
        )
        for key in sorted(appearances)
    ]
    return ResilienceReport(entries=entries)
