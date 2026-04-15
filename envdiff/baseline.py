"""Baseline snapshot support: save and load a .env diff baseline for future comparisons."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envdiff.comparator import DiffResult

_DEFAULT_BASELINE = ".envdiff-baseline.json"


def save_baseline(result: DiffResult, path: Optional[str] = None) -> Path:
    """Serialise *result* to JSON and write it to *path*.

    Returns the resolved Path that was written.
    """
    dest = Path(path or _DEFAULT_BASELINE)
    payload = {
        "only_in_a": {k: v for k, v in result.only_in_a.items()},
        "only_in_b": {k: v for k, v in result.only_in_b.items()},
        "mismatched": {
            k: {"a": pair[0], "b": pair[1]}
            for k, pair in result.mismatched.items()
        },
    }
    dest.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return dest


def load_baseline(path: Optional[str] = None) -> DiffResult:
    """Read a previously saved baseline and return it as a :class:`DiffResult`."""
    src = Path(path or _DEFAULT_BASELINE)
    if not src.exists():
        raise FileNotFoundError(f"Baseline file not found: {src}")
    raw = json.loads(src.read_text(encoding="utf-8"))
    mismatched = {
        k: (v["a"], v["b"]) for k, v in raw.get("mismatched", {}).items()
    }
    return DiffResult(
        only_in_a=raw.get("only_in_a", {}),
        only_in_b=raw.get("only_in_b", {}),
        mismatched=mismatched,
    )


def diff_against_baseline(
    current: DiffResult, baseline: DiffResult
) -> DiffResult:
    """Return only the *new* differences that are not present in *baseline*."""
    only_in_a = {
        k: v
        for k, v in current.only_in_a.items()
        if k not in baseline.only_in_a
    }
    only_in_b = {
        k: v
        for k, v in current.only_in_b.items()
        if k not in baseline.only_in_b
    }
    mismatched = {
        k: v
        for k, v in current.mismatched.items()
        if k not in baseline.mismatched
    }
    return DiffResult(
        only_in_a=only_in_a,
        only_in_b=only_in_b,
        mismatched=mismatched,
    )
