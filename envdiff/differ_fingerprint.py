"""Fingerprint a DiffResult for change detection and caching."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Dict

from envdiff.comparator import DiffResult


@dataclass
class Fingerprint:
    hex: str
    components: Dict[str, str]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Fingerprint):
            return NotImplemented
        return self.hex == other.hex

    def as_dict(self) -> dict:
        return {"hex": self.hex, "components": self.components}


def _stable_hash(data: object) -> str:
    raw = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def fingerprint_diff(result: DiffResult) -> Fingerprint:
    """Return a short fingerprint that uniquely identifies a DiffResult."""
    only_a = _stable_hash(sorted(result.only_in_a))
    only_b = _stable_hash(sorted(result.only_in_b))
    mismatched = _stable_hash(
        {k: (str(v[0]), str(v[1])) for k, v in sorted(result.mismatched.items())}
    )
    combined = _stable_hash({"a": only_a, "b": only_b, "m": mismatched})
    return Fingerprint(
        hex=combined,
        components={"only_in_a": only_a, "only_in_b": only_b, "mismatched": mismatched},
    )


def fingerprints_match(a: DiffResult, b: DiffResult) -> bool:
    """Return True when two DiffResults produce the same fingerprint."""
    return fingerprint_diff(a) == fingerprint_diff(b)
