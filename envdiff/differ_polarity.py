"""Polarity analysis: classify each key's diff status as positive, negative, or neutral
across a sequence of DiffResult snapshots.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict

from envdiff.comparator import DiffResult


@dataclass
class PolarityEntry:
    key: str
    positive: int   # times key was present and matched
    negative: int   # times key was missing or mismatched
    total: int

    @property
    def polarity_ratio(self) -> float:
        """Fraction of appearances that were positive (0.0 – 1.0)."""
        if self.total == 0:
            return 1.0
        return self.positive / self.total

    @property
    def dominant(self) -> str:
        r = self.polarity_ratio
        if r >= 0.75:
            return "positive"
        if r <= 0.25:
            return "negative"
        return "neutral"

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"PolarityEntry(key={self.key!r}, dominant={self.dominant!r}, "
            f"ratio={self.polarity_ratio:.2f})"
        )

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "positive": self.positive,
            "negative": self.negative,
            "total": self.total,
            "polarity_ratio": round(self.polarity_ratio, 4),
            "dominant": self.dominant,
        }


@dataclass
class PolarityReport:
    entries: List[PolarityEntry] = field(default_factory=list)

    def positive_keys(self) -> List[PolarityEntry]:
        return [e for e in self.entries if e.dominant == "positive"]

    def negative_keys(self) -> List[PolarityEntry]:
        return [e for e in self.entries if e.dominant == "negative"]

    def neutral_keys(self) -> List[PolarityEntry]:
        return [e for e in self.entries if e.dominant == "neutral"]

    def as_dict(self) -> dict:
        return {
            "entries": [e.as_dict() for e in self.entries],
            "positive_count": len(self.positive_keys()),
            "negative_count": len(self.negative_keys()),
            "neutral_count": len(self.neutral_keys()),
        }


def polarity_diff(results: List[DiffResult]) -> PolarityReport:
    """Compute polarity for every key seen across *results*."""
    positive: Dict[str, int] = {}
    negative: Dict[str, int] = {}
    total: Dict[str, int] = {}

    for r in results:
        all_keys = set(r.only_in_a) | set(r.only_in_b) | set(r.mismatched) | set(r.matching)
        for key in all_keys:
            total[key] = total.get(key, 0) + 1
            if key in r.matching:
                positive[key] = positive.get(key, 0) + 1
            else:
                negative[key] = negative.get(key, 0) + 1

    entries = [
        PolarityEntry(
            key=k,
            positive=positive.get(k, 0),
            negative=negative.get(k, 0),
            total=total[k],
        )
        for k in sorted(total)
    ]
    return PolarityReport(entries=entries)
