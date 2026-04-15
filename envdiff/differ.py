"""Multi-file diff: compare more than two .env files at once."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set

from envdiff.parser import parse_env_file
from envdiff.comparator import compare, DiffResult


@dataclass
class MultiDiffResult:
    """Aggregated diff across N env files."""
    files: List[str]
    # key -> {filename: value_or_None}
    matrix: Dict[str, Dict[str, str | None]] = field(default_factory=dict)
    # keys that differ in at least one file
    differing_keys: Set[str] = field(default_factory=set)
    # pairwise diffs keyed by (a, b)
    pairwise: Dict[tuple, DiffResult] = field(default_factory=dict)


def multi_diff(*paths: str | Path) -> MultiDiffResult:
    """Parse each path and produce a MultiDiffResult."""
    str_paths = [str(p) for p in paths]
    parsed = {p: parse_env_file(p) for p in str_paths}

    all_keys: Set[str] = set()
    for env in parsed.values():
        all_keys.update(env.keys())

    matrix: Dict[str, Dict[str, str | None]] = {}
    for key in sorted(all_keys):
        matrix[key] = {p: parsed[p].get(key) for p in str_paths}

    differing_keys: Set[str] = set()
    for key, vals in matrix.items():
        unique = set(vals.values())
        if len(unique) > 1:
            differing_keys.add(key)

    pairwise: Dict[tuple, DiffResult] = {}
    for i, a in enumerate(str_paths):
        for b in str_paths[i + 1 :]:
            pairwise[(a, b)] = compare(parsed[a], parsed[b])

    return MultiDiffResult(
        files=str_paths,
        matrix=matrix,
        differing_keys=differing_keys,
        pairwise=pairwise,
    )
