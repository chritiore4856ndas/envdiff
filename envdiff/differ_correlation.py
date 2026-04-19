"""Correlation analysis: which keys tend to change together across snapshots."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Tuple
from envdiff.comparator import DiffResult


@dataclass
class CorrelationPair:
    key_a: str
    key_b: str
    co_changes: int
    total_snapshots: int

    @property
    def correlation_ratio(self) -> float:
        if self.total_snapshots == 0:
            return 0.0
        return self.co_changes / self.total_snapshots

    def __repr__(self) -> str:
        return f"CorrelationPair({self.key_a!r}, {self.key_b!r}, ratio={self.correlation_ratio:.2f})"

    def as_dict(self) -> dict:
        return {
            "key_a": self.key_a,
            "key_b": self.key_b,
            "co_changes": self.co_changes,
            "total_snapshots": self.total_snapshots,
            "correlation_ratio": round(self.correlation_ratio, 4),
        }


@dataclass
class CorrelationReport:
    pairs: List[CorrelationPair] = field(default_factory=list)
    total_snapshots: int = 0

    def strongest(self, n: int = 5) -> List[CorrelationPair]:
        return sorted(self.pairs, key=lambda p: p.correlation_ratio, reverse=True)[:n]

    def as_dict(self) -> dict:
        return {
            "total_snapshots": self.total_snapshots,
            "pairs": [p.as_dict() for p in self.pairs],
        }


def _changed_keys(result: DiffResult) -> set:
    return set(result.only_in_a) | set(result.only_in_b) | set(result.mismatched)


def correlate_results(results: List[DiffResult]) -> CorrelationReport:
    if not results:
        return CorrelationReport()

    total = len(results)
    co_change: Dict[Tuple[str, str], int] = {}

    for result in results:
        changed = sorted(_changed_keys(result))
        for i, ka in enumerate(changed):
            for kb in changed[i + 1:]:
                pair = (ka, kb)
                co_change[pair] = co_change.get(pair, 0) + 1

    pairs = [
        CorrelationPair(key_a=ka, key_b=kb, co_changes=count, total_snapshots=total)
        for (ka, kb), count in co_change.items()
    ]
    pairs.sort(key=lambda p: p.correlation_ratio, reverse=True)
    return CorrelationReport(pairs=pairs, total_snapshots=total)
