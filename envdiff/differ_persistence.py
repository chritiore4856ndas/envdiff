"""Persistence analysis: tracks how long keys retain the same value across snapshots."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from envdiff.comparator import DiffResult


@dataclass
class PersistenceEntry:
    key: str
    unchanged_runs: int
    total_runs: int
    last_value: Optional[str]

    @property
    def persistence_rate(self) -> float:
        if self.total_runs == 0:
            return 1.0
        return self.unchanged_runs / self.total_runs

    @property
    def is_persistent(self) -> bool:
        return self.persistence_rate >= 0.8

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"PersistenceEntry(key={self.key!r}, rate={self.persistence_rate:.2f}, "
            f"unchanged={self.unchanged_runs}/{self.total_runs})"
        )

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "unchanged_runs": self.unchanged_runs,
            "total_runs": self.total_runs,
            "persistence_rate": round(self.persistence_rate, 4),
            "is_persistent": self.is_persistent,
            "last_value": self.last_value,
        }


@dataclass
class PersistenceReport:
    entries: list[PersistenceEntry] = field(default_factory=list)

    def volatile(self) -> list[PersistenceEntry]:
        """Keys that changed frequently (not persistent)."""
        return [e for e in self.entries if not e.is_persistent]

    def persistent(self) -> list[PersistenceEntry]:
        """Keys that stayed the same most of the time."""
        return [e for e in self.entries if e.is_persistent]

    def as_dict(self) -> dict:
        return {"entries": [e.as_dict() for e in self.entries]}


def persistence_diff(results: list[DiffResult]) -> PersistenceReport:
    """Analyse how persistently each key keeps its value across a list of DiffResults."""
    if not results:
        return PersistenceReport()

    all_keys: set[str] = set()
    for r in results:
        all_keys.update(r.only_in_a)
        all_keys.update(r.only_in_b)
        all_keys.update(r.mismatched.keys())
        all_keys.update(r.matching.keys())

    entries: list[PersistenceEntry] = []
    for key in sorted(all_keys):
        unchanged = 0
        last_value: Optional[str] = None
        for r in results:
            if key in r.matching:
                unchanged += 1
                last_value = r.matching[key]
            elif key in r.mismatched:
                last_value = r.mismatched[key][1]  # value from b
            elif key in r.only_in_a:
                last_value = None
            elif key in r.only_in_b:
                last_value = None
        entries.append(
            PersistenceEntry(
                key=key,
                unchanged_runs=unchanged,
                total_runs=len(results),
                last_value=last_value,
            )
        )

    return PersistenceReport(entries=entries)
