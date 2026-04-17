"""Bloom filter-inspired key presence tracker across multiple diff results."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set

from envdiff.comparator import DiffResult


@dataclass
class BloomEntry:
    key: str
    seen_in: int
    total: int

    @property
    def frequency(self) -> float:
        if self.total == 0:
            return 0.0
        return round(self.seen_in / self.total, 4)

    def __repr__(self) -> str:  # pragma: no cover
        return f"BloomEntry({self.key!r}, freq={self.frequency})"


@dataclass
class BloomReport:
    entries: List[BloomEntry] = field(default_factory=list)
    total_snapshots: int = 0

    def rare(self, threshold: float = 0.5) -> List[BloomEntry]:
        """Keys that appear in fewer than `threshold` fraction of snapshots."""
        return [e for e in self.entries if e.frequency < threshold]

    def common(self, threshold: float = 0.9) -> List[BloomEntry]:
        """Keys that appear in at least `threshold` fraction of snapshots."""
        return [e for e in self.entries if e.frequency >= threshold]

    def as_dict(self) -> dict:
        return {
            "total_snapshots": self.total_snapshots,
            "entries": [
                {"key": e.key, "seen_in": e.seen_in, "frequency": e.frequency}
                for e in self.entries
            ],
        }


def bloom_diff(results: List[DiffResult]) -> BloomReport:
    """Aggregate key presence across multiple DiffResult snapshots."""
    if not results:
        return BloomReport()

    counts: Dict[str, int] = {}
    total = len(results)

    for result in results:
        all_keys: Set[str] = (
            set(result.only_in_a)
            | set(result.only_in_b)
            | set(result.mismatched)
            | set(result.matching)
        )
        for key in all_keys:
            counts[key] = counts.get(key, 0) + 1

    entries = sorted(
        [BloomEntry(key=k, seen_in=v, total=total) for k, v in counts.items()],
        key=lambda e: (-e.seen_in, e.key),
    )
    return BloomReport(entries=entries, total_snapshots=total)
