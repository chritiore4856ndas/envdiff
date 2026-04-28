"""Flux analysis: measures the rate of change between consecutive diff snapshots."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from envdiff.comparator import DiffResult


@dataclass
class FluxEntry:
    key: str
    change_count: int
    total_transitions: int

    @property
    def flux_rate(self) -> float:
        if self.total_transitions == 0:
            return 0.0
        return self.change_count / self.total_transitions

    @property
    def is_flux(self) -> bool:
        return self.flux_rate > 0.5

    def __repr__(self) -> str:  # pragma: no cover
        return f"FluxEntry(key={self.key!r}, rate={self.flux_rate:.2f})"

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "change_count": self.change_count,
            "total_transitions": self.total_transitions,
            "flux_rate": round(self.flux_rate, 4),
            "is_flux": self.is_flux,
        }


@dataclass
class FluxReport:
    entries: List[FluxEntry] = field(default_factory=list)

    @property
    def high_flux(self) -> List[FluxEntry]:
        return [e for e in self.entries if e.is_flux]

    @property
    def most_volatile(self) -> Optional[FluxEntry]:
        return max(self.entries, key=lambda e: e.flux_rate, default=None)

    @property
    def average_flux(self) -> float:
        if not self.entries:
            return 0.0
        return sum(e.flux_rate for e in self.entries) / len(self.entries)

    def as_dict(self) -> dict:
        return {
            "entries": [e.as_dict() for e in self.entries],
            "average_flux": round(self.average_flux, 4),
            "most_volatile": self.most_volatile.key if self.most_volatile else None,
        }


def flux_diff(results: List[DiffResult]) -> FluxReport:
    """Compute flux for each key across a sequence of DiffResults."""
    if not results:
        return FluxReport()

    all_keys: set[str] = set()
    for r in results:
        all_keys.update(r.only_in_a)
        all_keys.update(r.only_in_b)
        all_keys.update(r.mismatched.keys())
        all_keys.update(r.matching.keys())

    transitions = max(len(results) - 1, 1)
    entries = []
    for key in sorted(all_keys):
        changes = 0
        for i in range(1, len(results)):
            prev = results[i - 1]
            curr = results[i]
            prev_problematic = key in prev.only_in_a or key in prev.only_in_b or key in prev.mismatched
            curr_problematic = key in curr.only_in_a or key in curr.only_in_b or key in curr.mismatched
            if prev_problematic != curr_problematic or (
                prev_problematic and curr_problematic
                and prev.mismatched.get(key) != curr.mismatched.get(key)
            ):
                changes += 1
        entries.append(FluxEntry(key=key, change_count=changes, total_transitions=transitions))

    return FluxReport(entries=entries)
