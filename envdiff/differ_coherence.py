"""Coherence analysis: measures how consistently keys appear with matching values across multiple diff results."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from envdiff.comparator import DiffResult


@dataclass
class CoherenceEntry:
    key: str
    appearances: int
    matching: int

    def coherence_rate(self) -> float:
        if self.appearances == 0:
            return 1.0
        return self.matching / self.appearances

    def is_coherent(self, threshold: float = 0.8) -> bool:
        return self.coherence_rate() >= threshold

    def __repr__(self) -> str:
        return (
            f"CoherenceEntry(key={self.key!r}, appearances={self.appearances}, "
            f"matching={self.matching}, rate={self.coherence_rate():.2f})"
        )

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "appearances": self.appearances,
            "matching": self.matching,
            "coherence_rate": round(self.coherence_rate(), 4),
            "is_coherent": self.is_coherent(),
        }


@dataclass
class CoherenceReport:
    entries: List[CoherenceEntry] = field(default_factory=list)

    def incoherent(self, threshold: float = 0.8) -> List[CoherenceEntry]:
        return [e for e in self.entries if not e.is_coherent(threshold)]

    def most_coherent(self) -> Optional[CoherenceEntry]:
        if not self.entries:
            return None
        return max(self.entries, key=lambda e: e.coherence_rate())

    def least_coherent(self) -> Optional[CoherenceEntry]:
        if not self.entries:
            return None
        return min(self.entries, key=lambda e: e.coherence_rate())

    def average_rate(self) -> float:
        if not self.entries:
            return 1.0
        return sum(e.coherence_rate() for e in self.entries) / len(self.entries)

    def as_dict(self) -> dict:
        return {
            "entries": [e.as_dict() for e in self.entries],
            "average_rate": round(self.average_rate(), 4),
            "incoherent_count": len(self.incoherent()),
        }


def coherence_diff(results: List[DiffResult]) -> CoherenceReport:
    """Compute coherence for each key across multiple DiffResult snapshots."""
    if not results:
        return CoherenceReport()

    all_keys: set[str] = set()
    for r in results:
        all_keys.update(r.only_in_a)
        all_keys.update(r.only_in_b)
        all_keys.update(r.mismatched.keys())
        all_keys.update(r.matching.keys())

    entries: List[CoherenceEntry] = []
    for key in sorted(all_keys):
        appearances = sum(
            1 for r in results
            if key in r.only_in_a or key in r.only_in_b
            or key in r.mismatched or key in r.matching
        )
        matching = sum(1 for r in results if key in r.matching)
        entries.append(CoherenceEntry(key=key, appearances=appearances, matching=matching))

    return CoherenceReport(entries=entries)
