"""Signature-based change detection: stable string fingerprint per key across envs."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.comparator import DiffResult


@dataclass
class SignatureEntry:
    key: str
    signature: str  # hex digest of sorted values seen
    value_set: List[str]
    stable: bool  # True when all non-None values are identical

    def __repr__(self) -> str:
        return f"SignatureEntry({self.key!r}, stable={self.stable})"

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "signature": self.signature,
            "value_set": self.value_set,
            "stable": self.stable,
        }


@dataclass
class SignatureReport:
    entries: List[SignatureEntry] = field(default_factory=list)

    @property
    def unstable(self) -> List[SignatureEntry]:
        return [e for e in self.entries if not e.stable]

    @property
    def stable(self) -> List[SignatureEntry]:
        return [e for e in self.entries if e.stable]

    def as_dict(self) -> dict:
        return {
            "total": len(self.entries),
            "stable_count": len(self.stable),
            "unstable_count": len(self.unstable),
            "entries": [e.as_dict() for e in self.entries],
        }


def _sig(values: List[str]) -> str:
    blob = "|".join(sorted(values))
    return hashlib.sha1(blob.encode()).hexdigest()[:12]


def signature_results(results: List[DiffResult]) -> SignatureReport:
    """Build a SignatureReport across multiple DiffResult snapshots."""
    key_values: Dict[str, List[str]] = {}

    for r in results:
        all_keys = set(r.only_in_a) | set(r.only_in_b) | set(r.mismatched) | set(r.matching)
        for k in all_keys:
            val_a = r.matching.get(k) or r.mismatched.get(k, (None, None))[0] if k in r.matching or k in r.mismatched else None
            val_b = r.mismatched.get(k, (None, None))[1] if k in r.mismatched else None
            for v in (val_a, val_b):
                if v is not None:
                    key_values.setdefault(k, []).append(v)

    entries = []
    for key, vals in sorted(key_values.items()):
        unique = list(dict.fromkeys(vals))
        entries.append(SignatureEntry(
            key=key,
            signature=_sig(unique),
            value_set=unique,
            stable=len(unique) == 1,
        ))

    return SignatureReport(entries=entries)
