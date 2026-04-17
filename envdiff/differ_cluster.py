"""Group keys across multiple DiffResults into clusters by similarity of change patterns."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.comparator import DiffResult


@dataclass
class ClusterEntry:
    key: str
    pattern: str  # e.g. 'missing_in_b', 'missing_in_a', 'mismatched', 'ok'
    count: int

    def __repr__(self) -> str:
        return f"ClusterEntry({self.key!r}, pattern={self.pattern!r}, count={self.count})"


@dataclass
class ClusterReport:
    clusters: Dict[str, List[ClusterEntry]] = field(default_factory=dict)

    def keys_in(self, pattern: str) -> List[str]:
        return [e.key for e in self.clusters.get(pattern, [])]

    def as_dict(self) -> dict:
        return {
            pattern: [{"key": e.key, "count": e.count} for e in entries]
            for pattern, entries in self.clusters.items()
        }


def _key_pattern(key: str, results: List[DiffResult]) -> str:
    """Determine the dominant change pattern for a key across results."""
    counts: Dict[str, int] = defaultdict(int)
    for r in results:
        if key in r.only_in_a:
            counts["missing_in_b"] += 1
        elif key in r.only_in_b:
            counts["missing_in_a"] += 1
        elif key in r.mismatched:
            counts["mismatched"] += 1
        else:
            counts["ok"] += 1
    return max(counts, key=lambda k: counts[k])


def cluster_diff(results: List[DiffResult]) -> ClusterReport:
    """Cluster all keys from multiple DiffResults by their dominant change pattern."""
    if not results:
        return ClusterReport()

    all_keys: set = set()
    for r in results:
        all_keys |= r.only_in_a | r.only_in_b | set(r.mismatched) | set(r.matching)

    pattern_counts: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for key in all_keys:
        pattern = _key_pattern(key, results)
        count = sum(
            1 for r in results
            if key in r.only_in_a or key in r.only_in_b
            or key in r.mismatched
        )
        pattern_counts[pattern][key] = count

    clusters: Dict[str, List[ClusterEntry]] = {}
    for pattern, key_map in pattern_counts.items():
        entries = [
            ClusterEntry(key=k, pattern=pattern, count=c)
            for k, c in key_map.items()
        ]
        entries.sort(key=lambda e: (-e.count, e.key))
        clusters[pattern] = entries

    return ClusterReport(clusters=clusters)
