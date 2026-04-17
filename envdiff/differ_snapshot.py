"""Snapshot diffing: compare current env files against a saved snapshot."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envdiff.comparator import DiffResult, compare
from envdiff.parser import parse_env_file


@dataclass
class SnapshotEntry:
    path: str
    diff: DiffResult

    def is_clean(self) -> bool:
        return not self.diff.only_in_a and not self.diff.only_in_b and not self.diff.mismatched

    def as_dict(self) -> dict:
        return {
            "path": self.path,
            "only_in_a": list(self.diff.only_in_a),
            "only_in_b": list(self.diff.only_in_b),
            "mismatched": list(self.diff.mismatched),
            "clean": self.is_clean(),
        }


@dataclass
class SnapshotReport:
    entries: List[SnapshotEntry] = field(default_factory=list)

    def is_clean(self) -> bool:
        return all(e.is_clean() for e in self.entries)

    def as_dict(self) -> dict:
        return {"clean": self.is_clean(), "entries": [e.as_dict() for e in self.entries]}


def _snapshot_path(store: Path, name: str) -> Path:
    return store / f"{name}.snapshot.json"


def save_snapshot(store: Path, name: str, env_paths: List[str]) -> Path:
    store.mkdir(parents=True, exist_ok=True)
    data: Dict[str, Optional[str]] = {}
    for p in env_paths:
        data.update(parse_env_file(Path(p)))
    dest = _snapshot_path(store, name)
    dest.write_text(json.dumps(data, indent=2))
    return dest


def load_snapshot(store: Path, name: str) -> Dict[str, Optional[str]]:
    p = _snapshot_path(store, name)
    if not p.exists():
        raise FileNotFoundError(f"Snapshot '{name}' not found in {store}")
    return json.loads(p.read_text())


def diff_against_snapshot(store: Path, name: str, env_paths: List[str]) -> SnapshotReport:
    baseline = load_snapshot(store, name)
    entries: List[SnapshotEntry] = []
    for p in env_paths:
        current = parse_env_file(Path(p))
        diff = compare(baseline, current)
        entries.append(SnapshotEntry(path=p, diff=diff))
    return SnapshotReport(entries=entries)
