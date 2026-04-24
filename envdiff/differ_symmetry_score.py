"""Compute a symmetry score across multiple DiffResult snapshots.

A symmetry score measures how evenly keys are distributed across environments
— a perfectly symmetric set of envs has the same keys everywhere.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from envdiff.comparator import DiffResult


@dataclass
class SymmetryScoreEntry:
    env_pair: str
    total_keys: int
    shared_keys: int
    symmetry_score: float  # 0.0 – 1.0

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"SymmetryScoreEntry({self.env_pair!r}, "
            f"score={self.symmetry_score:.2f})"
        )

    def as_dict(self) -> dict:
        return {
            "env_pair": self.env_pair,
            "total_keys": self.total_keys,
            "shared_keys": self.shared_keys,
            "symmetry_score": round(self.symmetry_score, 4),
        }


@dataclass
class SymmetryScoreReport:
    entries: List[SymmetryScoreEntry] = field(default_factory=list)

    def average_score(self) -> float:
        if not self.entries:
            return 1.0
        return sum(e.symmetry_score for e in self.entries) / len(self.entries)

    def lowest(self) -> SymmetryScoreEntry | None:
        if not self.entries:
            return None
        return min(self.entries, key=lambda e: e.symmetry_score)

    def as_dict(self) -> dict:
        return {
            "average_score": round(self.average_score(), 4),
            "entries": [e.as_dict() for e in self.entries],
        }


def symmetry_score_results(
    results: List[DiffResult],
    labels: List[str] | None = None,
) -> SymmetryScoreReport:
    """Build a SymmetryScoreReport from a list of DiffResult objects.

    Each DiffResult represents a pairwise comparison.  The label for the pair
    is taken from *labels* when provided, otherwise "env_N" is generated.
    """
    if not results:
        return SymmetryScoreReport()

    entries: List[SymmetryScoreEntry] = []
    for idx, result in enumerate(results):
        label = labels[idx] if labels and idx < len(labels) else f"env_{idx}"
        all_keys = (
            set(result.only_in_a)
            | set(result.only_in_b)
            | set(result.mismatched)
            | set(result.matching)
        )
        total = len(all_keys)
        shared = len(set(result.matching))
        score = shared / total if total > 0 else 1.0
        entries.append(
            SymmetryScoreEntry(
                env_pair=label,
                total_keys=total,
                shared_keys=shared,
                symmetry_score=score,
            )
        )

    return SymmetryScoreReport(entries=entries)
