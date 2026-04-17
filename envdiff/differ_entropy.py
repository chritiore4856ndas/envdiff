"""Entropy analysis: measure value diversity across multiple diff results."""
from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.comparator import DiffResult


@dataclass
class EntropyEntry:
    key: str
    unique_values: int
    total_seen: int
    entropy: float

    def __repr__(self) -> str:  # pragma: no cover
        return f"EntropyEntry({self.key!r}, entropy={self.entropy:.3f})"

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "unique_values": self.unique_values,
            "total_seen": self.total_seen,
            "entropy": round(self.entropy, 6),
        }


@dataclass
class EntropyReport:
    entries: List[EntropyEntry] = field(default_factory=list)

    def most_diverse(self, n: int = 5) -> List[EntropyEntry]:
        return sorted(self.entries, key=lambda e: e.entropy, reverse=True)[:n]

    def uniform_keys(self) -> List[EntropyEntry]:
        """Keys whose value never changes (entropy == 0) across snapshots."""
        return [e for e in self.entries if e.entropy == 0.0]

    def as_dict(self) -> dict:
        return {"entries": [e.as_dict() for e in self.entries]}


def _shannon(counts: List[int]) -> float:
    total = sum(counts)
    if total == 0:
        return 0.0
    return -sum((c / total) * math.log2(c / total) for c in counts if c > 0)


def entropy_diff(results: List[DiffResult]) -> EntropyReport:
    """Compute value-entropy per key across a list of DiffResult snapshots."""
    value_map: Dict[str, List[Optional[str]]] = {}

    for result in results:
        for key, val in result.mismatched.items():
            value_map.setdefault(key, []).extend([val[0], val[1]])
        for key in result.only_in_a:
            value_map.setdefault(key, []).append(None)
        for key in result.only_in_b:
            value_map.setdefault(key, []).append(None)

    entries: List[EntropyEntry] = []
    for key, values in value_map.items():
        counts = list(Counter(values).values())
        ent = _shannon(counts)
        entries.append(EntropyEntry(
            key=key,
            unique_values=len(set(values)),
            total_seen=len(values),
            entropy=ent,
        ))

    entries.sort(key=lambda e: e.entropy, reverse=True)
    return EntropyReport(entries=entries)
