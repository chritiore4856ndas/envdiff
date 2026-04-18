"""Track key lineage across multiple diff results — renamed, added, removed."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from envdiff.comparator import DiffResult


@dataclass
class LineageEntry:
    key: str
    first_seen: int  # index of result where key first appeared
    last_seen: int
    status_history: List[str]  # per-result status: 'match','missing_b','missing_a','mismatch'

    def __repr__(self) -> str:
        return f"LineageEntry({self.key!r}, spans={self.first_seen}-{self.last_seen})"

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "status_history": self.status_history,
            "lifespan": self.last_seen - self.first_seen + 1,
        }


@dataclass
class LineageReport:
    entries: Dict[str, LineageEntry] = field(default_factory=dict)

    def ephemeral(self, max_lifespan: int = 1) -> List[LineageEntry]:
        """Keys that appeared in only `max_lifespan` or fewer snapshots."""
        return [e for e in self.entries.values() if (e.last_seen - e.first_seen + 1) <= max_lifespan]

    def persistent(self, min_lifespan: int = 2) -> List[LineageEntry]:
        return [e for e in self.entries.values() if (e.last_seen - e.first_seen + 1) >= min_lifespan]

    def as_dict(self) -> dict:
        return {k: v.as_dict() for k, v in self.entries.items()}


def _status(key: str, result: DiffResult) -> Optional[str]:
    if key in result.only_in_a:
        return "missing_b"
    if key in result.only_in_b:
        return "missing_a"
    if key in result.mismatched:
        return "mismatch"
    if key in result.matching:
        return "match"
    return None


def build_lineage(results: List[DiffResult]) -> LineageReport:
    report = LineageReport()
    for idx, result in enumerate(results):
        all_keys = (
            set(result.only_in_a)
            | set(result.only_in_b)
            | set(result.mismatched)
            | set(result.matching)
        )
        for key in all_keys:
            st = _status(key, result)
            if key not in report.entries:
                report.entries[key] = LineageEntry(
                    key=key, first_seen=idx, last_seen=idx, status_history=[st]
                )
            else:
                entry = report.entries[key]
                entry.last_seen = idx
                entry.status_history.append(st)
    return report
