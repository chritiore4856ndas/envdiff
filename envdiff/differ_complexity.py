"""Complexity analysis across multiple diff results."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from envdiff.comparator import DiffResult


@dataclass
class ComplexityEntry:
    env_label: str
    total_keys: int
    issues: int
    complexity_score: float  # 0.0 = simple, 1.0 = maximally complex

    def is_complex(self, threshold: float = 0.4) -> bool:
        return self.complexity_score >= threshold

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"ComplexityEntry({self.env_label!r}, score={self.complexity_score:.2f})"
        )

    def as_dict(self) -> dict:
        return {
            "env": self.env_label,
            "total_keys": self.total_keys,
            "issues": self.issues,
            "complexity_score": round(self.complexity_score, 4),
            "is_complex": self.is_complex(),
        }


@dataclass
class ComplexityReport:
    entries: List[ComplexityEntry] = field(default_factory=list)

    def most_complex(self) -> Optional[ComplexityEntry]:
        return max(self.entries, key=lambda e: e.complexity_score, default=None)

    def average_score(self) -> float:
        if not self.entries:
            return 0.0
        return sum(e.complexity_score for e in self.entries) / len(self.entries)

    def as_dict(self) -> dict:
        return {
            "entries": [e.as_dict() for e in self.entries],
            "average_score": round(self.average_score(), 4),
            "most_complex": self.most_complex().env_label if self.most_complex() else None,
        }


def complexity_diff(
    results: List[DiffResult],
    labels: Optional[List[str]] = None,
) -> ComplexityReport:
    """Compute a complexity score for each diff result."""
    entries: List[ComplexityEntry] = []
    for idx, result in enumerate(results):
        label = labels[idx] if labels and idx < len(labels) else f"env_{idx}"
        all_keys = (
            result.only_in_a.keys()
            | result.only_in_b.keys()
            | result.mismatched.keys()
            | result.matching.keys()
        )
        total = len(all_keys)
        issues = (
            len(result.only_in_a)
            + len(result.only_in_b)
            + len(result.mismatched)
        )
        score = issues / total if total > 0 else 0.0
        entries.append(
            ComplexityEntry(
                env_label=label,
                total_keys=total,
                issues=issues,
                complexity_score=round(score, 4),
            )
        )
    return ComplexityReport(entries=entries)
