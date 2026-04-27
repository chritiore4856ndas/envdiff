"""Topology analysis: how keys are distributed across a set of diff results."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.comparator import DiffResult


@dataclass
class TopologyEntry:
    key: str
    present_in: List[str]  # env labels where key exists
    absent_in: List[str]   # env labels where key is missing

    @property
    def presence_rate(self) -> float:
        total = len(self.present_in) + len(self.absent_in)
        return len(self.present_in) / total if total else 1.0

    @property
    def is_universal(self) -> bool:
        return len(self.absent_in) == 0

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"TopologyEntry(key={self.key!r}, "
            f"presence_rate={self.presence_rate:.2f})"
        )

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "present_in": self.present_in,
            "absent_in": self.absent_in,
            "presence_rate": round(self.presence_rate, 4),
            "is_universal": self.is_universal,
        }


@dataclass
class TopologyReport:
    entries: List[TopologyEntry] = field(default_factory=list)

    @property
    def universal_keys(self) -> List[TopologyEntry]:
        return [e for e in self.entries if e.is_universal]

    @property
    def fragmented_keys(self) -> List[TopologyEntry]:
        return [e for e in self.entries if not e.is_universal]

    @property
    def most_absent(self) -> Optional[TopologyEntry]:
        if not self.entries:
            return None
        return min(self.entries, key=lambda e: e.presence_rate)

    def as_dict(self) -> dict:
        return {
            "entries": [e.as_dict() for e in self.entries],
            "universal_count": len(self.universal_keys),
            "fragmented_count": len(self.fragmented_keys),
        }


def topology_diff(results: Dict[str, DiffResult]) -> TopologyReport:
    """Analyse key presence topology across named diff results."""
    if not results:
        return TopologyReport()

    all_keys: set = set()
    for r in results.values():
        all_keys |= set(r.only_in_a) | set(r.only_in_b) | set(r.mismatched) | set(r.matching)

    entries: List[TopologyEntry] = []
    for key in sorted(all_keys):
        present: List[str] = []
        absent: List[str] = []
        for label, result in results.items():
            all_in_result = (
                set(result.only_in_a)
                | set(result.only_in_b)
                | set(result.mismatched)
                | set(result.matching)
            )
            if key in all_in_result:
                present.append(label)
            else:
                absent.append(label)
        entries.append(TopologyEntry(key=key, present_in=present, absent_in=absent))

    return TopologyReport(entries=entries)
