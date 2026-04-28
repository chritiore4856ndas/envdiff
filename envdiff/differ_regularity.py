"""Regularity analysis across multiple diff results.

Measures how consistently each key appears and changes across a series
of diff snapshots. A key is considered "regular" if its change pattern
is predictable (either always stable or always changing).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence

from envdiff.comparator import DiffResult


@dataclass
class RegularityEntry:
    key: str
    appearances: int       # number of results where the key was present
    change_count: int      # number of results where the key was differing
    total: int             # total number of results
    regularity_rate: float # 1.0 = perfectly regular (never or always changes)

    def is_regular(self, threshold: float = 0.8) -> bool:
        return self.regularity_rate >= threshold

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"RegularityEntry(key={self.key!r}, "
            f"regularity={self.regularity_rate:.2f}, "
            f"changes={self.change_count}/{self.appearances})"
        )

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "appearances": self.appearances,
            "change_count": self.change_count,
            "total": self.total,
            "regularity_rate": round(self.regularity_rate, 4),
        }


@dataclass
class RegularityReport:
    entries: List[RegularityEntry] = field(default_factory=list)

    def irregular(self, threshold: float = 0.8) -> List[RegularityEntry]:
        """Return entries that are NOT regular (unpredictable change pattern)."""
        return [e for e in self.entries if not e.is_regular(threshold)]

    def most_irregular(self) -> Optional[RegularityEntry]:
        """Return the entry with the lowest regularity rate."""
        if not self.entries:
            return None
        return min(self.entries, key=lambda e: e.regularity_rate)

    @property
    def average_rate(self) -> float:
        if not self.entries:
            return 1.0
        return sum(e.regularity_rate for e in self.entries) / len(self.entries)

    def as_dict(self) -> dict:
        return {
            "average_regularity_rate": round(self.average_rate, 4),
            "entries": [e.as_dict() for e in self.entries],
        }


def regularity_diff(results: Sequence[DiffResult]) -> RegularityReport:
    """Compute regularity of each key across a sequence of DiffResults.

    Regularity is defined as how close the change rate is to either 0.0
    (never changes) or 1.0 (always changes). A key that changes 50% of
    the time is maximally irregular.

    Args:
        results: Ordered sequence of DiffResult snapshots.

    Returns:
        RegularityReport with one entry per unique key seen.
    """
    if not results:
        return RegularityReport()

    total = len(results)

    # Collect per-key statistics
    appearances: dict[str, int] = {}
    change_count: dict[str, int] = {}

    for result in results:
        differing_keys = (
            set(result.only_in_a)
            | set(result.only_in_b)
            | set(result.mismatched)
        )
        all_keys = (
            set(result.only_in_a)
            | set(result.only_in_b)
            | set(result.mismatched)
            | set(result.matching)
        )
        for key in all_keys:
            appearances[key] = appearances.get(key, 0) + 1
            if key in differing_keys:
                change_count[key] = change_count.get(key, 0) + 1

    entries: list[RegularityEntry] = []
    for key in sorted(appearances):
        app = appearances[key]
        changes = change_count.get(key, 0)

        if app == 0:
            rate = 1.0
        else:
            change_ratio = changes / app
            # Regularity: distance from 0.5 mapped to [0, 1]
            # 0.0 change_ratio -> 1.0 regularity (always stable)
            # 1.0 change_ratio -> 1.0 regularity (always changing)
            # 0.5 change_ratio -> 0.0 regularity (maximally unpredictable)
            rate = abs(change_ratio - 0.5) * 2.0

        entries.append(
            RegularityEntry(
                key=key,
                appearances=app,
                change_count=changes,
                total=total,
                regularity_rate=round(rate, 4),
            )
        )

    return RegularityReport(entries=entries)
