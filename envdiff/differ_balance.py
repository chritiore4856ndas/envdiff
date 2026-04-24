"""Balance analysis: measures how evenly keys are distributed across envs."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence

from envdiff.comparator import DiffResult


@dataclass
class BalanceEntry:
    env_name: str
    total_keys: int
    missing_keys: int
    extra_keys: int
    mismatch_keys: int

    @property
    def balance_score(self) -> float:
        """1.0 = perfectly balanced, 0.0 = fully unbalanced."""
        if self.total_keys == 0:
            return 1.0
        issues = self.missing_keys + self.extra_keys + self.mismatch_keys
        return max(0.0, 1.0 - issues / self.total_keys)

    @property
    def is_balanced(self) -> bool:
        return self.balance_score >= 1.0

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"BalanceEntry({self.env_name!r}, score={self.balance_score:.2f})"
        )

    def as_dict(self) -> dict:
        return {
            "env_name": self.env_name,
            "total_keys": self.total_keys,
            "missing_keys": self.missing_keys,
            "extra_keys": self.extra_keys,
            "mismatch_keys": self.mismatch_keys,
            "balance_score": round(self.balance_score, 4),
            "is_balanced": self.is_balanced,
        }


@dataclass
class BalanceReport:
    entries: List[BalanceEntry] = field(default_factory=list)

    def unbalanced(self) -> List[BalanceEntry]:
        return [e for e in self.entries if not e.is_balanced]

    def as_dict(self) -> dict:
        return {"entries": [e.as_dict() for e in self.entries]}


def balance_results(
    results: Sequence[tuple[str, DiffResult]]
) -> BalanceReport:
    """Given (env_name, DiffResult) pairs, compute a BalanceReport."""
    entries: List[BalanceEntry] = []
    for env_name, result in results:
        all_keys = (
            set(result.only_in_a)
            | set(result.only_in_b)
            | set(result.mismatched)
        )
        total = len(all_keys) or 1  # avoid division by zero in score
        entries.append(
            BalanceEntry(
                env_name=env_name,
                total_keys=len(all_keys),
                missing_keys=len(result.only_in_a),
                extra_keys=len(result.only_in_b),
                mismatch_keys=len(result.mismatched),
            )
        )
    return BalanceReport(entries=entries)
