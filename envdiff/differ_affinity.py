"""Affinity analysis: which keys tend to share the same status across snapshots."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Tuple

from envdiff.comparator import DiffResult


@dataclass
class AffinityPair:
    key_a: str
    key_b: str
    co_occurrences: int
    total: int

    def affinity_ratio(self) -> float:
        return self.co_occurrences / self.total if self.total else 0.0

    def __repr__(self) -> str:  # pragma: no cover
        return f"AffinityPair({self.key_a!r}, {self.key_b!r}, ratio={self.affinity_ratio():.2f})"

    def as_dict(self) -> dict:
        return {
            "key_a": self.key_a,
            "key_b": self.key_b,
            "co_occurrences": self.co_occurrences,
            "total": self.total,
            "affinity_ratio": round(self.affinity_ratio(), 4),
        }


@dataclass
class AffinityReport:
    pairs: List[AffinityPair] = field(default_factory=list)
    total_snapshots: int = 0

    def strong(self, threshold: float = 0.8) -> List[AffinityPair]:
        return [p for p in self.pairs if p.affinity_ratio() >= threshold]

    def as_dict(self) -> dict:
        return {
            "total_snapshots": self.total_snapshots,
            "pairs": [p.as_dict() for p in self.pairs],
        }


def _problematic_keys(result: DiffResult) -> set:
    """Return keys that are missing or mismatched in this snapshot."""
    return set(result.only_in_a) | set(result.only_in_b) | set(result.mismatched)


def affinity_diff(results: List[DiffResult]) -> AffinityReport:
    """Compute how often pairs of keys share the same problematic status."""
    if not results:
        return AffinityReport()

    all_keys: set = set()
    snapshots: List[set] = []
    for r in results:
        prob = _problematic_keys(r)
        all_keys |= prob
        snapshots.append(prob)

    keys = sorted(all_keys)
    co_counts: Dict[Tuple[str, str], int] = {}

    for snap in snapshots:
        for i, ka in enumerate(keys):
            for kb in keys[i + 1 :]:
                if ka in snap and kb in snap:
                    co_counts[(ka, kb)] = co_counts.get((ka, kb), 0) + 1

    pairs = [
        AffinityPair(
            key_a=ka,
            key_b=kb,
            co_occurrences=count,
            total=len(results),
        )
        for (ka, kb), count in sorted(co_counts.items(), key=lambda x: -x[1])
    ]

    return AffinityReport(pairs=pairs, total_snapshots=len(results))
