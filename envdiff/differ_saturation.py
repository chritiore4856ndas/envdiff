"""Saturation analysis: measures how "full" each env is relative to the union of all keys."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence

from envdiff.comparator import DiffResult


@dataclass
class SaturationEntry:
    env_name: str
    present: int
    total: int

    @property
    def saturation_rate(self) -> float:
        return self.present / self.total if self.total else 1.0

    @property
    def is_saturated(self) -> bool:
        return self.saturation_rate >= 1.0

    def __repr__(self) -> str:
        return (
            f"SaturationEntry(env={self.env_name!r}, "
            f"present={self.present}, total={self.total}, "
            f"rate={self.saturation_rate:.2f})"
        )

    def as_dict(self) -> dict:
        return {
            "env": self.env_name,
            "present": self.present,
            "total": self.total,
            "saturation_rate": round(self.saturation_rate, 4),
            "is_saturated": self.is_saturated,
        }


@dataclass
class SaturationReport:
    entries: List[SaturationEntry] = field(default_factory=list)

    def least_saturated(self) -> List[SaturationEntry]:
        return sorted(self.entries, key=lambda e: e.saturation_rate)

    def as_dict(self) -> dict:
        return {"entries": [e.as_dict() for e in self.entries]}


def saturation_diff(
    results: Sequence[DiffResult],
    env_names: Sequence[str] | None = None,
) -> SaturationReport:
    """Compute per-env saturation across a collection of DiffResults.

    Each DiffResult represents a pairwise comparison between env A and env B.
    We collect the union of all keys seen and then count how many each env has.
    """
    if not results:
        return SaturationReport()

    names = list(env_names) if env_names else [f"env_{i}" for i in range(len(results) + 1)]

    # Build per-env key sets from pairwise results.
    # results[i] compares names[i] vs names[i+1].
    env_keys: dict[str, set[str]] = {n: set() for n in names}

    for i, result in enumerate(results):
        a_name = names[i] if i < len(names) else f"env_{i}"
        b_name = names[i + 1] if (i + 1) < len(names) else f"env_{i+1}"
        all_keys = (
            set(result.only_in_a)
            | set(result.only_in_b)
            | set(result.mismatched)
            | set(result.matching)
        )
        env_keys.setdefault(a_name, set()).update(result.only_in_a)
        env_keys.setdefault(a_name, set()).update(result.mismatched)
        env_keys.setdefault(a_name, set()).update(result.matching)
        env_keys.setdefault(b_name, set()).update(result.only_in_b)
        env_keys.setdefault(b_name, set()).update(result.mismatched)
        env_keys.setdefault(b_name, set()).update(result.matching)

    union_keys = set().union(*env_keys.values())
    total = len(union_keys)

    entries = [
        SaturationEntry(env_name=name, present=len(keys), total=total)
        for name, keys in env_keys.items()
    ]
    return SaturationReport(entries=entries)
