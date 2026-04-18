"""Detect keys that always change together across snapshots."""
from __future__ import annotations
from dataclasses import dataclass, field
from itertools import combinations
from typing import Sequence
from envdiff.comparator import DiffResult


@dataclass
class CouplingPair:
    key_a: str
    key_b: str
    co_changes: int
    total_snapshots: int

    def coupling_ratio(self) -> float:
        if self.total_snapshots == 0:
            return 0.0
        return self.co_changes / self.total_snapshots

    def __repr__(self) -> str:
        return f"CouplingPair({self.key_a!r}, {self.key_b!r}, ratio={self.coupling_ratio():.2f})"

    def as_dict(self) -> dict:
        return {
            "key_a": self.key_a,
            "key_b": self.key_b,
            "co_changes": self.co_changes,
            "total_snapshots": self.total_snapshots,
            "coupling_ratio": round(self.coupling_ratio(), 4),
        }


@dataclass
class CouplingReport:
    pairs: list[CouplingPair] = field(default_factory=list)
    total_snapshots: int = 0

    def strong(self, threshold: float = 0.8) -> list[CouplingPair]:
        return [p for p in self.pairs if p.coupling_ratio() >= threshold]

    def as_dict(self) -> dict:
        return {
            "total_snapshots": self.total_snapshots,
            "pairs": [p.as_dict() for p in self.pairs],
        }


def _differing_keys(result: DiffResult) -> set[str]:
    keys: set[str] = set()
    keys.update(result.only_in_a)
    keys.update(result.only_in_b)
    keys.update(result.mismatched.keys())
    return keys


def coupling_report(results: Sequence[DiffResult]) -> CouplingReport:
    if not results:
        return CouplingReport()

    all_keys: set[str] = set()
    per_snapshot: list[set[str]] = []
    for r in results:
        changed = _differing_keys(r)
        all_keys.update(changed)
        per_snapshot.append(changed)

    co_change: dict[tuple[str, str], int] = {}
    for snap in per_snapshot:
        for a, b in combinations(sorted(snap), 2):
            co_change[(a, b)] = co_change.get((a, b), 0) + 1

    pairs = [
        CouplingPair(a, b, count, len(results))
        for (a, b), count in sorted(co_change.items(), key=lambda x: -x[1])
    ]
    return CouplingReport(pairs=pairs, total_snapshots=len(results))
