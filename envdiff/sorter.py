"""Utilities for sorting and grouping DiffResult entries."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from envdiff.comparator import DiffResult


@dataclass
class GroupedDiff:
    """DiffResult entries grouped by category."""

    missing_in_b: List[str]   # keys only in A (missing from B)
    missing_in_a: List[str]   # keys only in B (missing from A)
    mismatched: List[str]     # keys present in both but values differ

    @property
    def total(self) -> int:
        return len(self.missing_in_b) + len(self.missing_in_a) + len(self.mismatched)

    @property
    def is_clean(self) -> bool:
        """Return True when there are no differences across all buckets."""
        return self.total == 0


def group_diff(result: DiffResult, sort_keys: bool = True) -> GroupedDiff:
    """Split a DiffResult into three sorted buckets.

    Args:
        result: The DiffResult produced by ``compare``.
        sort_keys: When *True* (default) each bucket is sorted alphabetically.

    Returns:
        A :class:`GroupedDiff` with keys partitioned by difference type.
    """
    missing_in_b: List[str] = []
    missing_in_a: List[str] = []
    mismatched: List[str] = []

    for key in result.only_in_a:
        missing_in_b.append(key)

    for key in result.only_in_b:
        missing_in_a.append(key)

    for key in result.differing_keys:
        mismatched.append(key)

    if sort_keys:
        missing_in_b.sort()
        missing_in_a.sort()
        mismatched.sort()

    return GroupedDiff(
        missing_in_b=missing_in_b,
        missing_in_a=missing_in_a,
        mismatched=mismatched,
    )
