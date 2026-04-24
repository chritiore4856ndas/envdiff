"""Measure how dispersed (spread out) key differences are across multiple diff results."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence

from envdiff.comparator import DiffResult


@dataclass
class DispersionEntry:
    key: str
    appearances: int
    total: int

    @property
    def dispersion_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return self.appearances / self.total

    def __repr__(self) -> str:  # pragma: no cover
        return f"DispersionEntry({self.key!r}, rate={self.dispersion_rate:.2f})"

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "appearances": self.appearances,
            "total": self.total,
            "dispersion_rate": round(self.dispersion_rate, 4),
        }


@dataclass
class DispersionReport:
    entries: List[DispersionEntry] = field(default_factory=list)
    total_snapshots: int = 0

    def spread(self, threshold: float = 0.5) -> List[DispersionEntry]:
        """Return keys whose dispersion rate meets or exceeds *threshold*."""
        return [e for e in self.entries if e.dispersion_rate >= threshold]

    def as_dict(self) -> dict:
        return {
            "total_snapshots": self.total_snapshots,
            "entries": [e.as_dict() for e in self.entries],
        }


def dispersion_diff(results: Sequence[DiffResult]) -> DispersionReport:
    """Build a DispersionReport from a sequence of DiffResult objects."""
    if not results:
        return DispersionReport()

    total = len(results)
    counts: dict[str, int] = {}

    for result in results:
        problematic = (
            set(result.only_in_a)
            | set(result.only_in_b)
            | set(result.mismatched)
        )
        for key in problematic:
            counts[key] = counts.get(key, 0) + 1

    entries = [
        DispersionEntry(key=k, appearances=v, total=total)
        for k, v in sorted(counts.items(), key=lambda x: -x[1])
    ]
    return DispersionReport(entries=entries, total_snapshots=total)
