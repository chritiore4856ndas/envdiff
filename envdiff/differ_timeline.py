"""Timeline diff: show how a key's value changed across ordered snapshots."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class TimelineEntry:
    key: str
    values: List[Optional[str]]  # one per snapshot, None = absent

    def changed(self) -> bool:
        seen = [v for v in self.values if v is not None]
        return len(set(seen)) > 1 or len(seen) != len(self.values)

    def as_dict(self) -> dict:
        return {"key": self.key, "values": self.values, "changed": self.changed()}

    def __repr__(self) -> str:  # pragma: no cover
        return f"TimelineEntry(key={self.key!r}, values={self.values})"


@dataclass
class TimelineReport:
    labels: List[str]
    entries: List[TimelineEntry] = field(default_factory=list)

    def changed_keys(self) -> List[TimelineEntry]:
        return [e for e in self.entries if e.changed()]

    def stable_keys(self) -> List[TimelineEntry]:
        return [e for e in self.entries if not e.changed()]

    def as_dict(self) -> dict:
        return {
            "labels": self.labels,
            "entries": [e.as_dict() for e in self.entries],
        }


def build_timeline(snapshots: List[Dict[str, Optional[str]]], labels: Optional[List[str]] = None) -> TimelineReport:
    """Build a timeline report from an ordered list of key->value dicts."""
    if not snapshots:
        return TimelineReport(labels=labels or [])

    resolved_labels = labels if labels and len(labels) == len(snapshots) else [
        str(i) for i in range(len(snapshots))
    ]

    all_keys: List[str] = []
    seen: set = set()
    for snap in snapshots:
        for k in snap:
            if k not in seen:
                all_keys.append(k)
                seen.add(k)

    entries = [
        TimelineEntry(key=k, values=[snap.get(k) for snap in snapshots])
        for k in all_keys
    ]

    return TimelineReport(labels=resolved_labels, entries=entries)
