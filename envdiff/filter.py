"""Filtering utilities for DiffResult — exclude keys by prefix or pattern."""

from __future__ import annotations

import re
from typing import Iterable

from envdiff.comparator import DiffResult


def _matches_any(key: str, patterns: Iterable[str]) -> bool:
    """Return True if *key* matches any of the given glob-style or regex patterns."""
    for pattern in patterns:
        if re.fullmatch(pattern, key):
            return True
    return False


def filter_diff(
    result: DiffResult,
    *,
    exclude_patterns: Iterable[str] = (),
    include_patterns: Iterable[str] = (),
) -> DiffResult:
    """Return a new DiffResult with keys filtered out.

    Parameters
    ----------
    result:
        The original diff result.
    exclude_patterns:
        Keys matching any of these regex patterns are removed.
    include_patterns:
        When non-empty, only keys matching at least one pattern are kept.
    """
    exclude = list(exclude_patterns)
    include = list(include_patterns)

    def _keep(key: str) -> bool:
        if exclude and _matches_any(key, exclude):
            return False
        if include and not _matches_any(key, include):
            return False
        return True

    return DiffResult(
        only_in_a={k: v for k, v in result.only_in_a.items() if _keep(k)},
        only_in_b={k: v for k, v in result.only_in_b.items() if _keep(k)},
        mismatched={
            k: v for k, v in result.mismatched.items() if _keep(k)
        },
        common_keys={
            k for k in result.common_keys if _keep(k)
        },
    )
