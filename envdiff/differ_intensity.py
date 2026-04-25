"""Intensity analysis: measures how severe the diff is per environment pair."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from envdiff.comparator import DiffResult


@dataclass
class IntensityEntry:
    env_name: str
    total_keys: int
    issue_count: int

    @property
    def intensity_rate(self) -> float:
        if self.total_keys == 0:
            return 0.0
        return self.issue_count / self.total_keys

    @property
    def is_intense(self, threshold: float = 0.5) -> bool:
        return self.intensity_rate >= threshold

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"IntensityEntry(env={self.env_name!r}, "
            f"rate={self.intensity_rate:.2f}, issues={self.issue_count})"
        )

    def as_dict(self) -> dict:
        return {
            "env": self.env_name,
            "total_keys": self.total_keys,
            "issue_count": self.issue_count,
            "intensity_rate": round(self.intensity_rate, 4),
        }


@dataclass
class IntensityReport:
    entries: List[IntensityEntry] = field(default_factory=list)

    @property
    def most_intense(self) -> Optional[IntensityEntry]:
        if not self.entries:
            return None
        return max(self.entries, key=lambda e: e.intensity_rate)

    @property
    def average_rate(self) -> float:
        if not self.entries:
            return 0.0
        return sum(e.intensity_rate for e in self.entries) / len(self.entries)

    def as_dict(self) -> dict:
        return {
            "entries": [e.as_dict() for e in self.entries],
            "average_rate": round(self.average_rate, 4),
            "most_intense": self.most_intense.env_name if self.most_intense else None,
        }


def intensity_diff(results: List[DiffResult], env_names: List[str]) -> IntensityReport:
    """Compute intensity for each named environment based on paired DiffResults."""
    if not results or not env_names:
        return IntensityReport()

    issue_counts: dict[str, int] = {name: 0 for name in env_names}
    key_sets: dict[str, set] = {name: set() for name in env_names}

    for result in results:
        all_keys = (
            set(result.only_in_a)
            | set(result.only_in_b)
            | set(result.mismatched)
            | set(result.matching)
        )
        for name in env_names:
            key_sets[name].update(all_keys)

        for key in result.only_in_a:
            issue_counts[env_names[0]] += 1
        for key in result.only_in_b:
            issue_counts[env_names[-1]] += 1
        for key in result.mismatched:
            for name in env_names:
                issue_counts[name] += 1

    entries = [
        IntensityEntry(
            env_name=name,
            total_keys=len(key_sets[name]),
            issue_count=issue_counts[name],
        )
        for name in env_names
    ]
    return IntensityReport(entries=entries)
