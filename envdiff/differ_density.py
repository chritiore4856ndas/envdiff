"""Density analysis: measures how "full" each env file is relative to the union of all keys."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence

from envdiff.comparator import DiffResult


@dataclass
class DensityEntry:
    env_name: str
    present: int
    total: int

    def density_rate(self) -> float:
        return self.present / self.total if self.total else 1.0

    def is_dense(self, threshold: float = 0.8) -> bool:
        return self.density_rate() >= threshold

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"DensityEntry(env={self.env_name!r}, "
            f"present={self.present}, total={self.total}, "
            f"rate={self.density_rate():.2f})"
        )

    def as_dict(self) -> dict:
        return {
            "env": self.env_name,
            "present": self.present,
            "total": self.total,
            "density_rate": round(self.density_rate(), 4),
            "is_dense": self.is_dense(),
        }


@dataclass
class DensityReport:
    entries: List[DensityEntry] = field(default_factory=list)

    def sparse(self, threshold: float = 0.8) -> List[DensityEntry]:
        return [e for e in self.entries if not e.is_dense(threshold)]

    def as_dict(self) -> dict:
        return {"entries": [e.as_dict() for e in self.entries]}


def density_results(
    results: Sequence[DiffResult],
    names: Sequence[str] | None = None,
) -> DensityReport:
    if not results:
        return DensityReport()

    labels = list(names) if names else [f"env{i}" for i in range(len(results))]

    # union of all keys seen across every result
    all_keys: set[str] = set()
    for r in results:
        all_keys.update(r.only_in_a)
        all_keys.update(r.only_in_b)
        all_keys.update(r.mismatched.keys())
        all_keys.update(r.matching.keys())

    total = len(all_keys)
    entries: List[DensityEntry] = []

    for label, result in zip(labels, results):
        # keys present in "a" side: matching + only_in_a
        present_a = len(result.matching) + len(result.only_in_a)
        entries.append(DensityEntry(env_name=label, present=present_a, total=total))

    return DensityReport(entries=entries)
