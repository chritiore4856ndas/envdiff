"""Resonance analysis: detect keys whose diff status is consistently
correlated across multiple snapshot pairs."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence

from envdiff.comparator import DiffResult


@dataclass
class ResonanceEntry:
    key: str
    co_occurrences: int  # how many pairs both keys appear as problematic
    total_pairs: int

    @property
    def resonance_ratio(self) -> float:
        if self.total_pairs == 0:
            return 0.0
        return self.co_occurrences / self.total_pairs

    def __repr__(self) -> str:
        return (
            f"ResonanceEntry(key={self.key!r}, "
            f"ratio={self.resonance_ratio:.2f})"
        )

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "co_occurrences": self.co_occurrences,
            "total_pairs": self.total_pairs,
            "resonance_ratio": round(self.resonance_ratio, 4),
        }


@dataclass
class ResonanceReport:
    entries: List[ResonanceEntry] = field(default_factory=list)

    def resonant(self, threshold: float = 0.5) -> List[ResonanceEntry]:
        return [e for e in self.entries if e.resonance_ratio >= threshold]

    def as_dict(self) -> dict:
        return {"entries": [e.as_dict() for e in self.entries]}


def _problematic_keys(result: DiffResult) -> set:
    """Return all keys that are in any non-matching state."""
    return (
        set(result.only_in_a)
        | set(result.only_in_b)
        | set(result.mismatched)
    )


def resonance_diff(results: Sequence[DiffResult]) -> ResonanceReport:
    """Compute resonance across a sequence of DiffResults.

    A key is resonant if it tends to be problematic in the same snapshots
    as other keys — measured by co-occurrence count.
    """
    if not results:
        return ResonanceReport()

    problematic_per: List[set] = [_problematic_keys(r) for r in results]
    all_keys: set = set().union(*problematic_per)

    if not all_keys:
        return ResonanceReport()

    # For each key, count how many snapshots it appears as problematic
    co_counts: Dict[str, int] = {k: 0 for k in all_keys}
    for prob_set in problematic_per:
        for k in prob_set:
            co_counts[k] += 1

    total = len(results)
    entries = [
        ResonanceEntry(key=k, co_occurrences=v, total_pairs=total)
        for k, v in sorted(co_counts.items(), key=lambda x: -x[1])
    ]
    return ResonanceReport(entries=entries)
