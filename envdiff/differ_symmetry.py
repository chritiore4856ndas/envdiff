"""Symmetry analysis: measure how symmetric differences are across two envs."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from envdiff.comparator import DiffResult


@dataclass
class SymmetryReport:
    only_in_a: List[str] = field(default_factory=list)
    only_in_b: List[str] = field(default_factory=list)
    mismatched: List[str] = field(default_factory=list)
    symmetry_ratio: float = 1.0

    @property
    def is_symmetric(self) -> bool:
        """True when both sides are missing the same number of keys."""
        return len(self.only_in_a) == len(self.only_in_b)

    @property
    def total_issues(self) -> int:
        return len(self.only_in_a) + len(self.only_in_b) + len(self.mismatched)

    def as_dict(self) -> dict:
        return {
            "only_in_a": self.only_in_a,
            "only_in_b": self.only_in_b,
            "mismatched": self.mismatched,
            "symmetry_ratio": round(self.symmetry_ratio, 4),
            "is_symmetric": self.is_symmetric,
            "total_issues": self.total_issues,
        }


def symmetry_diff(result: DiffResult) -> SymmetryReport:
    """Compute symmetry report from a single DiffResult."""
    only_a = sorted(result.only_in_a)
    only_b = sorted(result.only_in_b)
    mismatched = sorted(result.mismatched)

    total = len(only_a) + len(only_b) + len(mismatched)
    all_keys = set(only_a) | set(only_b) | set(mismatched) | set(result.matching)
    universe = len(all_keys)

    if universe == 0:
        ratio = 1.0
    else:
        ratio = 1.0 - (total / universe)
        ratio = max(0.0, min(1.0, ratio))

    return SymmetryReport(
        only_in_a=only_a,
        only_in_b=only_b,
        mismatched=mismatched,
        symmetry_ratio=ratio,
    )
