"""Drift detection: compare a current DiffResult against a previous snapshot."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional, Set

from envdiff.comparator import DiffResult


@dataclass
class DriftReport:
    """Keys that appeared, disappeared, or changed between two diff snapshots."""
    appeared: Set[str] = field(default_factory=set)   # new issues since snapshot
    resolved: Set[str] = field(default_factory=set)   # issues fixed since snapshot
    changed: Dict[str, tuple] = field(default_factory=dict)  # key -> (old_val, new_val)

    @property
    def is_clean(self) -> bool:
        return not (self.appeared or self.resolved or self.changed)

    def as_dict(self) -> dict:
        return {
            "appeared": sorted(self.appeared),
            "resolved": sorted(self.resolved),
            "changed": {k: list(v) for k, v in sorted(self.changed.items())},
        }


def _snapshot_path(store_dir: Path, name: str) -> Path:
    store_dir.mkdir(parents=True, exist_ok=True)
    return store_dir / f"{name}.drift.json"


def save_snapshot(result: DiffResult, store_dir: Path, name: str) -> Path:
    """Persist a DiffResult as a named drift snapshot."""
    data = {
        "only_in_a": sorted(result.only_in_a),
        "only_in_b": sorted(result.only_in_b),
        "mismatched": {k: list(v) for k, v in sorted(result.mismatched.items())},
    }
    path = _snapshot_path(store_dir, name)
    path.write_text(json.dumps(data, indent=2))
    return path


def load_snapshot(store_dir: Path, name: str) -> Optional[DiffResult]:
    """Load a previously saved drift snapshot, or None if it doesn't exist."""
    path = _snapshot_path(store_dir, name)
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    return DiffResult(
        only_in_a=set(data.get("only_in_a", [])),
        only_in_b=set(data.get("only_in_b", [])),
        mismatched={k: tuple(v) for k, v in data.get("mismatched", {}).items()},
    )


def detect_drift(previous: DiffResult, current: DiffResult) -> DriftReport:
    """Return a DriftReport describing what changed between two DiffResults."""
    prev_issues: Set[str] = previous.only_in_a | previous.only_in_b | set(previous.mismatched)
    curr_issues: Set[str] = current.only_in_a | current.only_in_b | set(current.mismatched)

    appeared = curr_issues - prev_issues
    resolved = prev_issues - curr_issues

    changed: Dict[str, tuple] = {}
    for key in prev_issues & curr_issues:
        old_val = previous.mismatched.get(key)
        new_val = current.mismatched.get(key)
        if old_val != new_val and old_val is not None and new_val is not None:
            changed[key] = (old_val, new_val)

    return DriftReport(appeared=appeared, resolved=resolved, changed=changed)
