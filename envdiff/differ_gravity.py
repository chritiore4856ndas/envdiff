"""Gravity analysis: measures how strongly each key 'pulls' across environments.

A key has high gravity when it appears in many environments AND frequently
differs — it is both widespread and unstable.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence

from envdiff.comparator import DiffResult


@dataclass
class GravityEntry:
    key: str
    appearances: int
    issues: int
    total: int

    @property
    def gravity_score(self) -> float:
        """Score in [0, 1]: proportion of snapshots where the key is problematic."""
        if self.total == 0:
            return 0.0
        return self.issues / self.total

    @property
    def is_heavy(self) -> bool:
        return self.gravity_score >= 0.5

    def __repr__(self) -> str:
        return (
            f"GravityEntry(key={self.key!r}, appearances={self.appearances}, "
            f"issues={self.issues}, score={self.gravity_score:.2f})"
        )

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "appearances": self.appearances,
            "issues": self.issues,
            "total": self.total,
            "gravity_score": round(self.gravity_score, 4),
            "is_heavy": self.is_heavy,
        }


@dataclass
class GravityReport:
    entries: List[GravityEntry] = field(default_factory=list)

    def heavy(self) -> List[GravityEntry]:
        return [e for e in self.entries if e.is_heavy]

    def top(self, n: int = 5) -> List[GravityEntry]:
        return sorted(self.entries, key=lambda e: e.gravity_score, reverse=True)[:n]

    def as_dict(self) -> dict:
        return {"entries": [e.as_dict() for e in self.entries]}


def gravity_diff(results: Sequence[DiffResult]) -> GravityReport:
    """Compute gravity for every key seen across *results*."""
    if not results:
        return GravityReport()

    total = len(results)
    appearances: dict[str, int] = {}
    issues: dict[str, int] = {}

    for r in results:
        all_keys = set(r.only_in_a) | set(r.only_in_b) | set(r.mismatched) | set(r.matching)
        for k in all_keys:
            appearances[k] = appearances.get(k, 0) + 1
        for k in set(r.only_in_a) | set(r.only_in_b) | set(r.mismatched):
            issues[k] = issues.get(k, 0) + 1

    entries = [
        GravityEntry(
            key=k,
            appearances=appearances[k],
            issues=issues.get(k, 0),
            total=total,
        )
        for k in sorted(appearances)
    ]
    entries.sort(key=lambda e: e.gravity_score, reverse=True)
    return GravityReport(entries=entries)
