"""Measure value variance for each key across multiple diff results."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from envdiff.comparator import DiffResult


@dataclass
class VarianceEntry:
    key: str
    values: List[Optional[str]]
    unique_count: int
    is_stable: bool

    def __repr__(self) -> str:
        return f"<VarianceEntry key={self.key!r} unique={self.unique_count} stable={self.is_stable}>"

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "values": self.values,
            "unique_count": self.unique_count,
            "is_stable": self.is_stable,
        }


@dataclass
class VarianceReport:
    entries: List[VarianceEntry] = field(default_factory=list)

    def unstable(self) -> List[VarianceEntry]:
        return [e for e in self.entries if not e.is_stable]

    def stable(self) -> List[VarianceEntry]:
        return [e for e in self.entries if e.is_stable]

    def as_dict(self) -> dict:
        return {"entries": [e.as_dict() for e in self.entries]}


def variance_diff(results: List[DiffResult]) -> VarianceReport:
    if not results:
        return VarianceReport()

    all_keys: set = set()
    for r in results:
        all_keys.update(r.only_in_a)
        all_keys.update(r.only_in_b)
        all_keys.update(r.mismatched.keys())
        all_keys.update(r.matching.keys())

    entries: List[VarianceEntry] = []
    for key in sorted(all_keys):
        values: List[Optional[str]] = []
        for r in results:
            if key in r.matching:
                values.append(r.matching[key])
            elif key in r.mismatched:
                val_a, val_b = r.mismatched[key]
                values.extend([val_a, val_b])
            elif key in r.only_in_a or key in r.only_in_b:
                values.append(None)
            else:
                values.append(None)
        unique_count = len(set(str(v) for v in values))
        entries.append(VarianceEntry(
            key=key,
            values=values,
            unique_count=unique_count,
            is_stable=unique_count == 1,
        ))

    return VarianceReport(entries=entries)
