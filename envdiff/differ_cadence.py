"""Cadence analysis: measures how regularly each key changes across snapshots."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from envdiff.comparator import DiffResult


@dataclass
class CadenceEntry:
    key: str
    change_intervals: List[int]  # snapshot indices where a change occurred
    total_snapshots: int

    @property
    def change_count(self) -> int:
        return len(self.change_intervals)

    @property
    def cadence_rate(self) -> float:
        """Fraction of snapshots in which the key changed."""
        if self.total_snapshots == 0:
            return 0.0
        return self.change_count / self.total_snapshots

    @property
    def is_regular(self) -> bool:
        """True when the key changes in more than half the snapshots."""
        return self.cadence_rate > 0.5

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"CadenceEntry(key={self.key!r}, rate={self.cadence_rate:.2f}, "
            f"regular={self.is_regular})"
        )

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "change_count": self.change_count,
            "total_snapshots": self.total_snapshots,
            "cadence_rate": round(self.cadence_rate, 4),
            "is_regular": self.is_regular,
        }


@dataclass
class CadenceReport:
    entries: List[CadenceEntry] = field(default_factory=list)

    def regular(self) -> List[CadenceEntry]:
        return [e for e in self.entries if e.is_regular]

    def irregular(self) -> List[CadenceEntry]:
        return [e for e in self.entries if not e.is_regular]

    def as_dict(self) -> dict:
        return {
            "entries": [e.as_dict() for e in self.entries],
            "regular_count": len(self.regular()),
            "irregular_count": len(self.irregular()),
        }


def cadence_diff(results: List[DiffResult]) -> CadenceReport:
    """Compute cadence for every key seen across *results*."""
    if not results:
        return CadenceReport()

    all_keys: set[str] = set()
    for r in results:
        all_keys.update(r.only_in_a)
        all_keys.update(r.only_in_b)
        all_keys.update(r.mismatched.keys())
        all_keys.update(r.matching.keys())

    entries: List[CadenceEntry] = []
    for key in sorted(all_keys):
        intervals = [
            idx
            for idx, r in enumerate(results)
            if key in r.only_in_a
            or key in r.only_in_b
            or key in r.mismatched
        ]
        entries.append(
            CadenceEntry(
                key=key,
                change_intervals=intervals,
                total_snapshots=len(results),
            )
        )

    return CadenceReport(entries=entries)
