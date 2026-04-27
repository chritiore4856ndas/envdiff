"""Coverage analysis: how completely each env file covers the full key universe."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from envdiff.comparator import DiffResult


@dataclass
class CoverageEntry:
    env_name: str
    total_keys: int
    present_keys: int
    missing_keys: List[str] = field(default_factory=list)

    def coverage_rate(self) -> float:
        if self.total_keys == 0:
            return 1.0
        return self.present_keys / self.total_keys

    def is_complete(self, threshold: float = 1.0) -> bool:
        return self.coverage_rate() >= threshold

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"CoverageEntry(env={self.env_name!r}, "
            f"rate={self.coverage_rate():.2f}, "
            f"present={self.present_keys}/{self.total_keys})"
        )

    def as_dict(self) -> dict:
        return {
            "env": self.env_name,
            "total_keys": self.total_keys,
            "present_keys": self.present_keys,
            "coverage_rate": round(self.coverage_rate(), 4),
            "missing_keys": self.missing_keys,
        }


@dataclass
class CoverageReport:
    entries: List[CoverageEntry] = field(default_factory=list)

    def least_covered(self) -> Optional[CoverageEntry]:
        if not self.entries:
            return None
        return min(self.entries, key=lambda e: e.coverage_rate())

    def most_covered(self) -> Optional[CoverageEntry]:
        if not self.entries:
            return None
        return max(self.entries, key=lambda e: e.coverage_rate())

    def average_rate(self) -> float:
        if not self.entries:
            return 1.0
        return sum(e.coverage_rate() for e in self.entries) / len(self.entries)

    def as_dict(self) -> dict:
        return {
            "average_coverage_rate": round(self.average_rate(), 4),
            "entries": [e.as_dict() for e in self.entries],
        }


def coverage_diff(results: List[DiffResult], env_names: Optional[List[str]] = None) -> CoverageReport:
    """Given multiple DiffResults (each comparing env_a vs env_b), compute per-env coverage."""
    if not results:
        return CoverageReport()

    names = env_names or [f"env_{i}" for i in range(len(results) + 1)]

    # Build the universe of all keys across all results
    universe: set = set()
    for r in results:
        universe |= set(r.only_in_a) | set(r.only_in_b) | set(r.matching) | set(r.mismatched)

    total = len(universe)
    entries: List[CoverageEntry] = []

    for idx, r in enumerate(results):
        env_name = names[idx] if idx < len(names) else f"env_{idx}"
        missing = sorted(r.only_in_b)  # keys in b but not in a => a is missing them
        present = total - len(missing)
        entries.append(CoverageEntry(
            env_name=env_name,
            total_keys=total,
            present_keys=max(present, 0),
            missing_keys=missing,
        ))

    return CoverageReport(entries=entries)
