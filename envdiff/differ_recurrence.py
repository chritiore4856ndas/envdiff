"""Detect keys that recurrently appear as problematic across snapshots."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence

from envdiff.comparator import DiffResult


@dataclass
class RecurrenceEntry:
    key: str
    occurrences: int
    total: int

    @property
    def recurrence_rate(self) -> float:
        return self.occurrences / self.total if self.total else 0.0

    @property
    def is_recurrent(self) -> bool:
        return self.recurrence_rate >= 0.5

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"RecurrenceEntry(key={self.key!r}, "
            f"occurrences={self.occurrences}, "
            f"rate={self.recurrence_rate:.2f})"
        )

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "occurrences": self.occurrences,
            "total": self.total,
            "recurrence_rate": round(self.recurrence_rate, 4),
            "is_recurrent": self.is_recurrent,
        }


@dataclass
class RecurrenceReport:
    entries: List[RecurrenceEntry] = field(default_factory=list)
    total_snapshots: int = 0

    def recurrent(self) -> List[RecurrenceEntry]:
        return [e for e in self.entries if e.is_recurrent]

    def top(self, n: int = 5) -> List[RecurrenceEntry]:
        return sorted(self.entries, key=lambda e: e.recurrence_rate, reverse=True)[:n]

    def as_dict(self) -> dict:
        return {
            "total_snapshots": self.total_snapshots,
            "entries": [e.as_dict() for e in self.entries],
        }


def recurrence_diff(results: Sequence[DiffResult]) -> RecurrenceReport:
    """Count how often each key appears as problematic across results."""
    if not results:
        return RecurrenceReport(entries=[], total_snapshots=0)

    total = len(results)
    counter: dict[str, int] = {}

    for result in results:
        problematic = (
            set(result.only_in_a)
            | set(result.only_in_b)
            | set(result.mismatched)
        )
        for key in problematic:
            counter[key] = counter.get(key, 0) + 1

    entries = [
        RecurrenceEntry(key=k, occurrences=v, total=total)
        for k, v in sorted(counter.items(), key=lambda x: x[1], reverse=True)
    ]
    return RecurrenceReport(entries=entries, total_snapshots=total)
