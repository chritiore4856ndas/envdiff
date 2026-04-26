"""Maturity analysis: measures how "settled" each key is across snapshots.

A key is considered mature if it has been consistently present and stable
across a high proportion of the provided diff results.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from envdiff.comparator import DiffResult


@dataclass
class MaturityEntry:
    key: str
    appearances: int
    stable_count: int
    total: int

    @property
    def maturity_rate(self) -> float:
        if self.total == 0:
            return 1.0
        return self.stable_count / self.total

    @property
    def is_mature(self) -> bool:
        return self.maturity_rate >= 0.8

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"MaturityEntry(key={self.key!r}, rate={self.maturity_rate:.2f}, "
            f"mature={self.is_mature})"
        )

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "appearances": self.appearances,
            "stable_count": self.stable_count,
            "total": self.total,
            "maturity_rate": round(self.maturity_rate, 4),
            "is_mature": self.is_mature,
        }


@dataclass
class MaturityReport:
    entries: List[MaturityEntry] = field(default_factory=list)

    def immature(self) -> List[MaturityEntry]:
        return [e for e in self.entries if not e.is_mature]

    def mature(self) -> List[MaturityEntry]:
        return [e for e in self.entries if e.is_mature]

    @property
    def average_rate(self) -> float:
        if not self.entries:
            return 1.0
        return sum(e.maturity_rate for e in self.entries) / len(self.entries)

    def as_dict(self) -> dict:
        return {
            "entries": [e.as_dict() for e in self.entries],
            "average_rate": round(self.average_rate, 4),
        }


def maturity_diff(results: List[DiffResult]) -> MaturityReport:
    """Compute maturity for every key seen across *results*."""
    if not results:
        return MaturityReport()

    total = len(results)
    all_keys: set = set()
    for r in results:
        all_keys |= set(r.only_in_a) | set(r.only_in_b) | set(r.mismatched) | set(r.matching)

    entries: List[MaturityEntry] = []
    for key in sorted(all_keys):
        appearances = sum(
            1 for r in results
            if key in r.only_in_a or key in r.only_in_b
            or key in r.mismatched or key in r.matching
        )
        stable_count = sum(1 for r in results if key in r.matching)
        entries.append(MaturityEntry(key=key, appearances=appearances,
                                     stable_count=stable_count, total=total))

    entries.sort(key=lambda e: e.maturity_rate)
    return MaturityReport(entries=entries)
