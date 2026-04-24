"""Frequency analysis: how often each key appears across multiple diff results."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence

from envdiff.comparator import DiffResult


@dataclass
class FrequencyEntry:
    key: str
    appearances: int
    total: int

    @property
    def frequency_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return self.appearances / self.total

    def __repr__(self) -> str:  # pragma: no cover
        return f"FrequencyEntry({self.key!r}, {self.appearances}/{self.total})"

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "appearances": self.appearances,
            "total": self.total,
            "frequency_rate": round(self.frequency_rate, 4),
        }


@dataclass
class FrequencyReport:
    entries: List[FrequencyEntry] = field(default_factory=list)

    def common(self, threshold: float = 0.5) -> List[FrequencyEntry]:
        """Keys appearing in at least `threshold` fraction of results."""
        return [e for e in self.entries if e.frequency_rate >= threshold]

    def rare(self, threshold: float = 0.5) -> List[FrequencyEntry]:
        """Keys appearing in fewer than `threshold` fraction of results."""
        return [e for e in self.entries if e.frequency_rate < threshold]

    def as_dict(self) -> dict:
        return {"entries": [e.as_dict() for e in self.entries]}


def frequency_diff(results: Sequence[DiffResult]) -> FrequencyReport:
    """Count how often each key appears (in any diff set) across all results."""
    if not results:
        return FrequencyReport()

    total = len(results)
    counts: dict[str, int] = {}

    for result in results:
        all_keys = set(result.only_in_a) | set(result.only_in_b) | set(result.mismatched)
        for key in all_keys:
            counts[key] = counts.get(key, 0) + 1

    entries = [
        FrequencyEntry(key=k, appearances=v, total=total)
        for k, v in sorted(counts.items(), key=lambda x: -x[1])
    ]
    return FrequencyReport(entries=entries)
