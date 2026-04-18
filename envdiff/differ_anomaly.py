"""Detect anomalous keys — present in only one snapshot out of many."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict

from envdiff.comparator import DiffResult


@dataclass
class AnomalyEntry:
    key: str
    occurrences: int
    total: int

    @property
    def frequency(self) -> float:
        return self.occurrences / self.total if self.total else 0.0

    def __repr__(self) -> str:
        return f"<AnomalyEntry {self.key} {self.occurrences}/{self.total}>"

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "occurrences": self.occurrences,
            "total": self.total,
            "frequency": round(self.frequency, 4),
        }


@dataclass
class AnomalyReport:
    entries: List[AnomalyEntry] = field(default_factory=list)
    threshold: float = 0.2

    def anomalies(self) -> List[AnomalyEntry]:
        """Return entries whose frequency is at or below the threshold."""
        return [e for e in self.entries if e.frequency <= self.threshold]

    def as_dict(self) -> dict:
        return {
            "threshold": self.threshold,
            "entries": [e.as_dict() for e in self.entries],
            "anomalies": [e.as_dict() for e in self.anomalies()],
        }


def detect_anomalies(
    results: List[DiffResult], threshold: float = 0.2
) -> AnomalyReport:
    """Count how often each differing key appears across all results."""
    counts: Dict[str, int] = {}
    total = len(results)

    for result in results:
        seen = set(result.only_in_a) | set(result.only_in_b) | set(result.mismatched)
        for key in seen:
            counts[key] = counts.get(key, 0) + 1

    entries = [
        AnomalyEntry(key=k, occurrences=v, total=total)
        for k, v in sorted(counts.items(), key=lambda x: x[1])
    ]
    return AnomalyReport(entries=entries, threshold=threshold)
