"""Compute per-key change statistics across multiple diff runs."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Iterable

from envdiff.comparator import DiffResult


@dataclass
class KeyStats:
    key: str
    times_missing_in_b: int = 0
    times_missing_in_a: int = 0
    times_mismatched: int = 0

    @property
    def total_issues(self) -> int:
        return self.times_missing_in_a + self.times_missing_in_b + self.times_mismatched


@dataclass
class StatsResult:
    key_stats: dict[str, KeyStats] = field(default_factory=dict)

    def most_problematic(self, n: int = 5) -> list[KeyStats]:
        return sorted(
            self.key_stats.values(),
            key=lambda s: s.total_issues,
            reverse=True,
        )[:n]

    @property
    def total_issues(self) -> int:
        return sum(s.total_issues for s in self.key_stats.values())


def compute_stats(results: Iterable[DiffResult]) -> StatsResult:
    """Aggregate issue counts across multiple DiffResult objects."""
    stats: dict[str, KeyStats] = {}

    def _get(key: str) -> KeyStats:
        if key not in stats:
            stats[key] = KeyStats(key=key)
        return stats[key]

    for result in results:
        for key in result.only_in_a:
            _get(key).times_missing_in_b += 1
        for key in result.only_in_b:
            _get(key).times_missing_in_a += 1
        for key in result.mismatched:
            _get(key).times_mismatched += 1

    return StatsResult(key_stats=stats)


def format_stats(stats: StatsResult) -> str:
    if not stats.key_stats:
        return "No issues recorded."

    lines = ["Key Issue Statistics:", ""]
    for s in stats.most_problematic(n=len(stats.key_stats)):
        lines.append(
            f"  {s.key}: {s.total_issues} issue(s) "
            f"(missing_in_b={s.times_missing_in_b}, "
            f"missing_in_a={s.times_missing_in_a}, "
            f"mismatched={s.times_mismatched})"
        )
    lines.append(f"\nTotal issues: {stats.total_issues}")
    return "\n".join(lines)
