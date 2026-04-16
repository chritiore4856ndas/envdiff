"""Support for .envdiffignore files — skip keys matching listed patterns."""
from __future__ import annotations

import fnmatch
from pathlib import Path
from typing import Iterable

from envdiff.comparator import DiffResult


DEFAULT_IGNORE_FILE = ".envdiffignore"


def load_ignore_patterns(path: str | Path) -> list[str]:
    """Read patterns from an ignore file, skipping blanks and comments."""
    p = Path(path)
    if not p.exists():
        return []
    patterns: list[str] = []
    for line in p.read_text().splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            patterns.append(stripped)
    return patterns


def _matches(key: str, patterns: Iterable[str]) -> bool:
    return any(fnmatch.fnmatch(key, pat) for pat in patterns)


def apply_ignore(result: DiffResult, patterns: Iterable[str]) -> DiffResult:
    """Return a new DiffResult with ignored keys removed from all sets."""
    pats = list(patterns)
    if not pats:
        return result

    def drop(mapping: dict) -> dict:
        return {k: v for k, v in mapping.items() if not _matches(k, pats)}

    return DiffResult(
        only_in_a={k for k in result.only_in_a if not _matches(k, pats)},
        only_in_b={k for k in result.only_in_b if not _matches(k, pats)},
        mismatched=drop(result.mismatched),
        matching=drop(result.matching),
    )
