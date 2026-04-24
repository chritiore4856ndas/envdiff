"""Dominance analysis: which environment 'wins' most often across a set of diffs.

For each key that differs, we count how many times each env provides the
majority value.  An env is said to dominate a key when its value matches
the most-common value seen across all snapshots for that key.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Sequence

from envdiff.comparator import DiffResult


@dataclass
class DominanceEntry:
    env: str
    dominated_keys: List[str]
    dominated_count: int
    dominance_ratio: float

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"DominanceEntry(env={self.env!r}, "
            f"dominated={self.dominated_count}, "
            f"ratio={self.dominance_ratio:.2f})"
        )

    def as_dict(self) -> dict:
        return {
            "env": self.env,
            "dominated_keys": self.dominated_keys,
            "dominated_count": self.dominated_count,
            "dominance_ratio": round(self.dominance_ratio, 4),
        }


@dataclass
class DominanceReport:
    entries: List[DominanceEntry] = field(default_factory=list)
    total_contested_keys: int = 0

    def dominant_env(self) -> str | None:
        if not self.entries:
            return None
        return max(self.entries, key=lambda e: e.dominated_count).env

    def as_dict(self) -> dict:
        return {
            "dominant_env": self.dominant_env(),
            "total_contested_keys": self.total_contested_keys,
            "entries": [e.as_dict() for e in self.entries],
        }


def dominance_diff(
    results: Sequence[DiffResult],
    env_names: Sequence[str] | None = None,
) -> DominanceReport:
    """Compute which environment dominates the most contested keys.

    Each DiffResult is treated as a pairwise comparison between env A and
    env B.  *env_names* can provide explicit labels; defaults to
    ["env_0", "env_1", ...].
    """
    if not results:
        return DominanceReport()

    names: List[str]
    if env_names:
        names = list(env_names)
    else:
        names = [f"env_{i}" for i in range(len(results))]

    # key -> Counter of {value: count}
    value_counts: Dict[str, Counter] = defaultdict(Counter)
    # key -> {env: value}
    env_values: Dict[str, Dict[str, str | None]] = defaultdict(dict)

    for idx, result in enumerate(results):
        env = names[idx] if idx < len(names) else f"env_{idx}"
        all_keys = (
            set(result.only_in_a)
            | set(result.only_in_b)
            | set(result.mismatched)
        )
        for key in all_keys:
            val = result.mismatched.get(key, (None, None))
            chosen = val[0] if val[0] is not None else val[1]
            value_counts[key][str(chosen)] += 1
            env_values[key][env] = chosen

    contested_keys = set(value_counts.keys())
    total_contested = len(contested_keys)

    dominated: Dict[str, List[str]] = defaultdict(list)

    for key, counter in value_counts.items():
        if not counter:
            continue
        majority_val, _ = counter.most_common(1)[0]
        for env, val in env_values[key].items():
            if str(val) == majority_val:
                dominated[env].append(key)

    entries: List[DominanceEntry] = []
    for env in names:
        keys = dominated.get(env, [])
        ratio = len(keys) / total_contested if total_contested else 0.0
        entries.append(
            DominanceEntry(
                env=env,
                dominated_keys=sorted(keys),
                dominated_count=len(keys),
                dominance_ratio=ratio,
            )
        )

    entries.sort(key=lambda e: e.dominated_count, reverse=True)
    return DominanceReport(entries=entries, total_contested_keys=total_contested)
