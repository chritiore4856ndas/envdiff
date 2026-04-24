"""Track the lifecycle stage of each key across multiple diff snapshots.

A key can be: new, stable, degrading, recovered, or removed.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional

from envdiff.comparator import DiffResult


@dataclass
class LifecycleEntry:
    key: str
    stage: str          # new | stable | degrading | recovered | removed
    first_seen: int     # snapshot index (0-based)
    last_seen: int
    issue_count: int    # number of snapshots where the key had a problem

    def __repr__(self) -> str:  # pragma: no cover
        return f"<LifecycleEntry {self.key!r} stage={self.stage}>"

    def as_dict(self) -> Dict:
        return {
            "key": self.key,
            "stage": self.stage,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "issue_count": self.issue_count,
        }


@dataclass
class LifecycleReport:
    entries: List[LifecycleEntry] = field(default_factory=list)

    def new_keys(self) -> List[LifecycleEntry]:
        return [e for e in self.entries if e.stage == "new"]

    def removed_keys(self) -> List[LifecycleEntry]:
        return [e for e in self.entries if e.stage == "removed"]

    def degrading_keys(self) -> List[LifecycleEntry]:
        return [e for e in self.entries if e.stage == "degrading"]

    def as_dict(self) -> Dict:
        return {"entries": [e.as_dict() for e in self.entries]}


def _is_problematic(key: str, result: DiffResult) -> bool:
    return (
        key in result.only_in_a
        or key in result.only_in_b
        or key in result.mismatched
    )


def lifecycle_diff(results: List[DiffResult]) -> LifecycleReport:
    if not results:
        return LifecycleReport()

    all_keys: set = set()
    for r in results:
        all_keys |= set(r.only_in_a) | set(r.only_in_b) | set(r.mismatched) | set(r.matching)

    entries: List[LifecycleEntry] = []
    n = len(results)

    for key in sorted(all_keys):
        present = [key in (set(r.only_in_a) | set(r.only_in_b) | set(r.mismatched) | set(r.matching)) for r in results]
        first_seen = next((i for i, p in enumerate(present) if p), 0)
        last_seen = max(i for i, p in enumerate(present) if p)
        issue_count = sum(1 for r in results if _is_problematic(key, r))

        appeared_late = first_seen > 0
        disappeared = last_seen < n - 1
        all_issues = issue_count == n
        any_issue = issue_count > 0
        prev_had_issue = issue_count > 0 and not _is_problematic(key, results[-1])

        if appeared_late:
            stage = "new"
        elif disappeared:
            stage = "removed"
        elif prev_had_issue:
            stage = "recovered"
        elif all_issues or (any_issue and issue_count >= n // 2 + 1):
            stage = "degrading"
        else:
            stage = "stable"

        entries.append(LifecycleEntry(
            key=key,
            stage=stage,
            first_seen=first_seen,
            last_seen=last_seen,
            issue_count=issue_count,
        ))

    return LifecycleReport(entries=entries)
