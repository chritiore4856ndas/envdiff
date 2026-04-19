"""Staleness detection: flag keys whose values haven't changed across all snapshots."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from envdiff.comparator import DiffResult


@dataclass
class StalenessEntry:
    key: str
    value: Optional[str]
    snapshots_seen: int
    is_stale: bool

    def __repr__(self) -> str:
        status = "stale" if self.is_stale else "active"
        return f"<StalenessEntry {self.key!r} {status} seen={self.snapshots_seen}>"

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "value": self.value,
            "snapshots_seen": self.snapshots_seen,
            "is_stale": self.is_stale,
        }


@dataclass
class StalenessReport:
    entries: List[StalenessEntry] = field(default_factory=list)

    def stale(self) -> List[StalenessEntry]:
        return [e for e in self.entries if e.is_stale]

    def active(self) -> List[StalenessEntry]:
        return [e for e in self.entries if not e.is_stale]

    def as_dict(self) -> dict:
        return {"entries": [e.as_dict() for e in self.entries]}


def staleness_diff(results: List[DiffResult]) -> StalenessReport:
    """A key is stale if it appears in every snapshot with the same value (no churn)."""
    if not results:
        return StalenessReport()

    key_values: Dict[str, List[Optional[str]]] = {}

    for result in results:
        all_keys = set(result.only_in_a) | set(result.only_in_b) | set(result.mismatched) | set(result.matching)
        for key in all_keys:
            if key not in key_values:
                key_values[key] = []
            if key in result.matching:
                key_values[key].append(result.matching[key])
            elif key in result.mismatched:
                key_values[key].append(result.mismatched[key][0])
            else:
                key_values[key].append(None)

    entries = []
    for key, values in sorted(key_values.items()):
        unique = set(v for v in values if v is not None)
        is_stale = len(unique) == 1 and len(values) == len(results)
        entries.append(StalenessEntry(
            key=key,
            value=values[0] if values else None,
            snapshots_seen=len(values),
            is_stale=is_stale,
        ))

    return StalenessReport(entries=entries)
