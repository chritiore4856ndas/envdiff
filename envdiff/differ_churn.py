"""Churn analysis: measures how frequently each key changes across snapshots."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence

from envdiff.comparator import DiffResult


@dataclass
class ChurnEntry:
    key: str
    changes: int
    snapshots: int

    @property
    def churn_rate(self) -> float:
        """Fraction of snapshot transitions where this key changed."""
        if self.snapshots == 0:
            return 0.0
        return self.changes / self.snapshots

    def __repr__(self) -> str:  # pragma: no cover
        return f"ChurnEntry({self.key!r}, rate={self.churn_rate:.2f})"

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "changes": self.changes,
            "snapshots": self.snapshots,
            "churn_rate": round(self.churn_rate, 4),
        }


@dataclass
class ChurnReport:
    entries: List[ChurnEntry] = field(default_factory=list)

    def high_churn(self, threshold: float = 0.5) -> List[ChurnEntry]:
        """Return entries whose churn_rate exceeds *threshold*."""
        return [e for e in self.entries if e.churn_rate > threshold]

    def as_dict(self) -> dict:
        return {"entries": [e.as_dict() for e in self.entries]}


def churn_diff(results: Sequence[DiffResult]) -> ChurnReport:
    """Compute churn for each key across a sequence of DiffResults.

    Each result is treated as one snapshot transition.  A key 'changes'
    in a transition when it appears in *only_in_a*, *only_in_b*, or
    *mismatched*.
    """
    if not results:
        return ChurnReport()

    all_keys: set[str] = set()
    for r in results:
        all_keys.update(r.only_in_a)
        all_keys.update(r.only_in_b)
        all_keys.update(r.mismatched.keys())
        all_keys.update(r.matching.keys())

    entries: List[ChurnEntry] = []
    total = len(results)
    for key in sorted(all_keys):
        changes = sum(
            1
            for r in results
            if key in r.only_in_a
            or key in r.only_in_b
            or key in r.mismatched
        )
        entries.append(ChurnEntry(key=key, changes=changes, snapshots=total))

    entries.sort(key=lambda e: (-e.churn_rate, e.key))
    return ChurnReport(entries=entries)
