"""Age-based diff analysis: flag keys that haven't changed across snapshots."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
import json
import os


@dataclass
class AgeEntry:
    key: str
    first_seen: str
    last_changed: str
    change_count: int

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "first_seen": self.first_seen,
            "last_changed": self.last_changed,
            "change_count": self.change_count,
        }


@dataclass
class AgeReport:
    entries: List[AgeEntry] = field(default_factory=list)

    def stale(self, min_changes: int = 1) -> List[AgeEntry]:
        """Return keys with fewer changes than min_changes."""
        return [e for e in self.entries if e.change_count < min_changes]

    def as_dict(self) -> dict:
        return {"entries": [e.as_dict() for e in self.entries]}


def _age_path(path: str) -> str:
    return path if path.endswith(".age.json") else path + ".age.json"


def load_age_data(path: str) -> Dict[str, dict]:
    p = _age_path(path)
    if not os.path.exists(p):
        return {}
    with open(p) as f:
        return json.load(f)


def save_age_data(path: str, data: Dict[str, dict]) -> None:
    with open(_age_path(path), "w") as f:
        json.dump(data, f, indent=2)


def record_age(path: str, current_values: Dict[str, Optional[str]]) -> AgeReport:
    """Update age tracking for keys and return an AgeReport."""
    now = datetime.utcnow().isoformat()
    data = load_age_data(path)
    entries = []

    for key, val in current_values.items():
        prev = data.get(key)
        if prev is None:
            data[key] = {
                "first_seen": now,
                "last_changed": now,
                "change_count": 1,
                "last_value": val,
            }
        else:
            changed = prev.get("last_value") != val
            data[key] = {
                "first_seen": prev["first_seen"],
                "last_changed": now if changed else prev["last_changed"],
                "change_count": prev["change_count"] + (1 if changed else 0),
                "last_value": val,
            }
        d = data[key]
        entries.append(AgeEntry(key, d["first_seen"], d["last_changed"], d["change_count"]))

    save_age_data(path, data)
    return AgeReport(entries=entries)
