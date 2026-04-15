"""Redact sensitive values in diff output before display or export."""
from __future__ import annotations

import re
from typing import Sequence

from envdiff.comparator import DiffResult

# Patterns that suggest a value is sensitive
_SENSITIVE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"password", re.IGNORECASE),
    re.compile(r"secret", re.IGNORECASE),
    re.compile(r"token", re.IGNORECASE),
    re.compile(r"api[_\-]?key", re.IGNORECASE),
    re.compile(r"private[_\-]?key", re.IGNORECASE),
    re.compile(r"auth", re.IGNORECASE),
    re.compile(r"credential", re.IGNORECASE),
]

REDACTED = "***REDACTED***"


def _is_sensitive(key: str, extra_patterns: Sequence[str] = ()) -> bool:
    """Return True if the key name looks sensitive."""
    patterns = list(_SENSITIVE_PATTERNS) + [
        re.compile(p, re.IGNORECASE) for p in extra_patterns
    ]
    return any(pat.search(key) for pat in patterns)


def redact_diff(
    result: DiffResult,
    extra_patterns: Sequence[str] = (),
) -> DiffResult:
    """Return a new DiffResult with sensitive values replaced by REDACTED."""

    def _redact_val(key: str, val: str | None) -> str | None:
        if val is None:
            return None
        return REDACTED if _is_sensitive(key, extra_patterns) else val

    redacted_mismatches: dict[str, tuple[str | None, str | None]] = {
        key: (_redact_val(key, a_val), _redact_val(key, b_val))
        for key, (a_val, b_val) in result.mismatches.items()
    }

    return DiffResult(
        only_in_a=result.only_in_a,
        only_in_b=result.only_in_b,
        mismatches=redacted_mismatches,
    )
