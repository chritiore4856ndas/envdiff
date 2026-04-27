"""Fidelity analysis: measures how faithfully each env reproduces the reference (first) env."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from envdiff.comparator import DiffResult


@dataclass
class FidelityEntry:
    env_name: str
    total_keys: int
    matching_keys: int
    missing_keys: int
    extra_keys: int
    mismatched_keys: int

    def fidelity_rate(self) -> float:
        if self.total_keys == 0:
            return 1.0
        return self.matching_keys / self.total_keys

    def is_faithful(self, threshold: float = 0.8) -> bool:
        return self.fidelity_rate() >= threshold

    def __repr__(self) -> str:
        return (
            f"FidelityEntry(env={self.env_name!r}, "
            f"rate={self.fidelity_rate():.2f}, "
            f"matching={self.matching_keys}/{self.total_keys})"
        )

    def as_dict(self) -> dict:
        return {
            "env": self.env_name,
            "total_keys": self.total_keys,
            "matching_keys": self.matching_keys,
            "missing_keys": self.missing_keys,
            "extra_keys": self.extra_keys,
            "mismatched_keys": self.mismatched_keys,
            "fidelity_rate": round(self.fidelity_rate(), 4),
            "is_faithful": self.is_faithful(),
        }


@dataclass
class FidelityReport:
    entries: List[FidelityEntry] = field(default_factory=list)

    def most_faithful(self) -> Optional[FidelityEntry]:
        if not self.entries:
            return None
        return max(self.entries, key=lambda e: e.fidelity_rate())

    def least_faithful(self) -> Optional[FidelityEntry]:
        if not self.entries:
            return None
        return min(self.entries, key=lambda e: e.fidelity_rate())

    def average_rate(self) -> float:
        if not self.entries:
            return 1.0
        return sum(e.fidelity_rate() for e in self.entries) / len(self.entries)

    def as_dict(self) -> dict:
        return {
            "entries": [e.as_dict() for e in self.entries],
            "average_fidelity_rate": round(self.average_rate(), 4),
            "most_faithful": self.most_faithful().env_name if self.most_faithful() else None,
            "least_faithful": self.least_faithful().env_name if self.least_faithful() else None,
        }


def fidelity_diff(results: List[DiffResult], env_names: List[str]) -> FidelityReport:
    """Compare each result against the union of all keys (reference universe)."""
    if not results:
        return FidelityReport()

    all_keys: set = set()
    for r in results:
        all_keys |= set(r.only_in_a) | set(r.only_in_b) | set(r.mismatched) | set(r.matching)

    total = len(all_keys)
    entries: List[FidelityEntry] = []

    for name, result in zip(env_names, results):
        matching = len(result.matching)
        missing = len(result.only_in_a)   # in reference but not here
        extra = len(result.only_in_b)     # here but not in reference
        mismatched = len(result.mismatched)
        entries.append(FidelityEntry(
            env_name=name,
            total_keys=total,
            matching_keys=matching,
            missing_keys=missing,
            extra_keys=extra,
            mismatched_keys=mismatched,
        ))

    return FidelityReport(entries=entries)
