"""Pivot a list of DiffResults into a per-key view across environments."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.comparator import DiffResult


@dataclass
class PivotRow:
    key: str
    values: Dict[str, Optional[str]] = field(default_factory=dict)
    statuses: Dict[str, str] = field(default_factory=dict)

    def __repr__(self) -> str:  # pragma: no cover
        return f"PivotRow(key={self.key!r}, statuses={self.statuses})"


@dataclass
class PivotReport:
    rows: List[PivotRow] = field(default_factory=list)
    env_names: List[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "envs": self.env_names,
            "rows": [
                {
                    "key": r.key,
                    "values": r.values,
                    "statuses": r.statuses,
                }
                for r in self.rows
            ],
        }


def pivot_results(
    results: Dict[str, DiffResult],
) -> PivotReport:
    """Build a pivot table from a mapping of env_name -> DiffResult.

    Each DiffResult is the comparison of that env against a reference.
    """
    env_names = list(results.keys())
    all_keys: set[str] = set()
    for dr in results.values():
        all_keys.update(dr.only_in_a)
        all_keys.update(dr.only_in_b)
        all_keys.update(dr.mismatched.keys())
        all_keys.update(dr.matching.keys())

    rows: List[PivotRow] = []
    for key in sorted(all_keys):
        row = PivotRow(key=key)
        for env, dr in results.items():
            if key in dr.matching:
                row.values[env] = dr.matching[key]
                row.statuses[env] = "match"
            elif key in dr.mismatched:
                row.values[env] = dr.mismatched[key][1]  # env value
                row.statuses[env] = "mismatch"
            elif key in dr.only_in_b:
                row.values[env] = dr.only_in_b[key]
                row.statuses[env] = "only_here"
            elif key in dr.only_in_a:
                row.values[env] = None
                row.statuses[env] = "missing"
            else:
                row.values[env] = None
                row.statuses[env] = "absent"
        rows.append(row)

    return PivotReport(rows=rows, env_names=env_names)
