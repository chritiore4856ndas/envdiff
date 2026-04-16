"""Merge two DiffResults into a single resolved env dict."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from envdiff.comparator import DiffResult


@dataclass
class MergeResult:
    resolved: Dict[str, Optional[str]]
    conflicts: Dict[str, tuple]  # key -> (val_a, val_b)

    @property
    def has_conflicts(self) -> bool:
        return bool(self.conflicts)

    def as_env_lines(self) -> list[str]:
        lines = []
        for key, val in sorted(self.resolved.items()):
            if val is None:
                lines.append(f"{key}=")
            else:
                lines.append(f"{key}={val}")
        return lines


def merge(
    result: DiffResult,
    prefer: str = "a",
    skip_conflicts: bool = False,
) -> MergeResult:
    """Merge env A and env B from a DiffResult.

    Args:
        result: output of compare()
        prefer: which side wins on mismatch — 'a' or 'b'
        skip_conflicts: if True, mismatched keys are omitted instead of resolved
    """
    if prefer not in ("a", "b"):
        raise ValueError("prefer must be 'a' or 'b'")

    resolved: Dict[str, Optional[str]] = {}
    conflicts: Dict[str, tuple] = {}

    # Keys only in A
    for key, val in result.only_in_a.items():
        resolved[key] = val

    # Keys only in B
    for key, val in result.only_in_b.items():
        resolved[key] = val

    # Matching keys
    for key, val in result.matching.items():
        resolved[key] = val

    # Mismatched keys
    for key, (val_a, val_b) in result.mismatched.items():
        conflicts[key] = (val_a, val_b)
        if not skip_conflicts:
            resolved[key] = val_a if prefer == "a" else val_b

    return MergeResult(resolved=resolved, conflicts=conflicts)
