"""Cohesion analysis: measures how consistently a key appears across all env snapshots."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence

from envdiff.comparator import DiffResult


@dataclass
class CohesionEntry:
    key: str
    appearances: int
    total: int

    @property
    def cohesion_ratio(self) -> float:
        """Fraction of snapshots the key appears in (present in either side)."""
        if self.total == 0:
            return 1.0
        return self.appearances / self.total

    @property
    def is_cohesive(self) -> bool:
        return self.cohesion_ratio >= 0.8

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"CohesionEntry(key={self.key!r}, "
            f"appearances={self.appearances}/{self.total}, "
            f"ratio={self.cohesion_ratio:.2f})"
        )

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "appearances": self.appearances,
            "total": self.total,
            "cohesion_ratio": round(self.cohesion_ratio, 4),
            "is_cohesive": self.is_cohesive,
        }


@dataclass
class CohesionReport:
    entries: List[CohesionEntry] = field(default_factory=list)

    def fragile(self) -> List[CohesionEntry]:
        """Keys that are NOT cohesive (appear in fewer than 80% of snapshots)."""
        return [e for e in self.entries if not e.is_cohesive]

    def as_dict(self) -> dict:
        return {"entries": [e.as_dict() for e in self.entries]}


def cohesion_diff(results: Sequence[DiffResult]) -> CohesionReport:
    """Compute cohesion for every key seen across all diff results."""
    if not results:
        return CohesionReport()

    total = len(results)
    key_appearances: dict[str, int] = {}

    for result in results:
        seen_in_snapshot: set[str] = set()
        seen_in_snapshot.update(result.only_in_a)
        seen_in_snapshot.update(result.only_in_b)
        seen_in_snapshot.update(result.mismatched.keys())
        seen_in_snapshot.update(result.matching.keys())
        for key in seen_in_snapshot:
            key_appearances[key] = key_appearances.get(key, 0) + 1

    entries = [
        CohesionEntry(key=k, appearances=v, total=total)
        for k, v in sorted(key_appearances.items())
    ]
    return CohesionReport(entries=entries)
