"""Compute key overlap statistics between two DiffResults."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Set

from envdiff.comparator import DiffResult


@dataclass
class OverlapReport:
    shared_keys: Set[str]
    only_in_a: Set[str]
    only_in_b: Set[str]
    mismatched: Set[str]
    matching: Set[str]

    @property
    def total_keys(self) -> int:
        return len(self.shared_keys | self.only_in_a | self.only_in_b)

    @property
    def overlap_ratio(self) -> float:
        """Fraction of all keys that appear in both files."""
        if self.total_keys == 0:
            return 1.0
        return len(self.shared_keys) / self.total_keys

    @property
    def match_ratio(self) -> float:
        """Fraction of shared keys whose values agree."""
        if not self.shared_keys:
            return 1.0
        return len(self.matching) / len(self.shared_keys)

    def as_dict(self) -> dict:
        return {
            "shared_keys": sorted(self.shared_keys),
            "only_in_a": sorted(self.only_in_a),
            "only_in_b": sorted(self.only_in_b),
            "mismatched": sorted(self.mismatched),
            "matching": sorted(self.matching),
            "total_keys": self.total_keys,
            "overlap_ratio": round(self.overlap_ratio, 4),
            "match_ratio": round(self.match_ratio, 4),
        }


def compute_overlap(result: DiffResult) -> OverlapReport:
    shared = set(result.mismatched) | set(
        k for k in result.only_in_a if k not in result.only_in_a
    )
    # shared = keys present in both = all keys minus exclusive ones
    all_keys = set(result.only_in_a) | set(result.only_in_b) | set(result.mismatched)
    only_a = set(result.only_in_a)
    only_b = set(result.only_in_b)
    mismatched = set(result.mismatched)
    shared_keys = all_keys - only_a - only_b
    matching = shared_keys - mismatched
    return OverlapReport(
        shared_keys=shared_keys,
        only_in_a=only_a,
        only_in_b=only_b,
        mismatched=mismatched,
        matching=matching,
    )
