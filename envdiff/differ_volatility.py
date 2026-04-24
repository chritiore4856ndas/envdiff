"""Volatility analysis: measures how frequently each key changes across snapshots."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional

from envdiff.comparator import DiffResult


@dataclass
class VolatilityEntry:
    key: str
    change_count: int
    snapshot_count: int

    @property
    def volatility_rate(self) -> float:
        if self.snapshot_count == 0:
            return 0.0
        return self.change_count / self.snapshot_count

    @property
    def is_volatile(self) -> bool:
        return self.volatility_rate > 0.5

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"VolatilityEntry(key={self.key!r}, rate={self.volatility_rate:.2f}, "
            f"volatile={self.is_volatile})"
        )

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "change_count": self.change_count,
            "snapshot_count": self.snapshot_count,
            "volatility_rate": round(self.volatility_rate, 4),
            "is_volatile": self.is_volatile,
        }


@dataclass
class VolatilityReport:
    entries: List[VolatilityEntry] = field(default_factory=list)

    def volatile(self) -> List[VolatilityEntry]:
        return [e for e in self.entries if e.is_volatile]

    def stable(self) -> List[VolatilityEntry]:
        return [e for e in self.entries if not e.is_volatile]

    def as_dict(self) -> dict:
        return {
            "entries": [e.as_dict() for e in self.entries],
            "volatile_count": len(self.volatile()),
            "stable_count": len(self.stable()),
        }


def volatility_diff(results: List[DiffResult]) -> VolatilityReport:
    """Compute per-key volatility across a sequence of DiffResult snapshots."""
    if not results:
        return VolatilityReport()

    change_counts: Dict[str, int] = {}
    seen_keys: Dict[str, int] = {}

    for result in results:
        all_keys = (
            set(result.only_in_a)
            | set(result.only_in_b)
            | set(result.mismatched)
            | set(result.matching)
        )
        for key in all_keys:
            seen_keys[key] = seen_keys.get(key, 0) + 1

        differing = set(result.only_in_a) | set(result.only_in_b) | set(result.mismatched)
        for key in differing:
            change_counts[key] = change_counts.get(key, 0) + 1

    entries = [
        VolatilityEntry(
            key=key,
            change_count=change_counts.get(key, 0),
            snapshot_count=seen_keys[key],
        )
        for key in sorted(seen_keys)
    ]

    return VolatilityReport(entries=entries)
