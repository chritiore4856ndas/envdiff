"""Momentum analysis: measures the rate of change acceleration across snapshots."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence

from envdiff.comparator import DiffResult


@dataclass
class MomentumEntry:
    key: str
    change_counts: List[int]  # per-window change counts
    acceleration: float       # second derivative of change rate

    def __repr__(self) -> str:  # pragma: no cover
        return f"MomentumEntry({self.key!r}, accel={self.acceleration:.3f})"

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "change_counts": self.change_counts,
            "acceleration": round(self.acceleration, 4),
        }


@dataclass
class MomentumReport:
    entries: List[MomentumEntry] = field(default_factory=list)

    def accelerating(self) -> List[MomentumEntry]:
        """Keys whose change rate is speeding up."""
        return [e for e in self.entries if e.acceleration > 0]

    def decelerating(self) -> List[MomentumEntry]:
        """Keys whose change rate is slowing down."""
        return [e for e in self.entries if e.acceleration < 0]

    def as_dict(self) -> dict:
        return {
            "entries": [e.as_dict() for e in self.entries],
            "accelerating": len(self.accelerating()),
            "decelerating": len(self.decelerating()),
        }


def _is_changed(key: str, result: DiffResult) -> bool:
    return (
        key in result.only_in_a
        or key in result.only_in_b
        or key in result.mismatched
    )


def momentum_diff(results: Sequence[DiffResult], window: int = 2) -> MomentumReport:
    """Compute momentum (acceleration of change rate) for each key.

    Splits *results* into windows of *window* size and counts changes per
    window, then computes the linear slope of those counts as acceleration.
    """
    if len(results) < 2:
        return MomentumReport()

    all_keys: set[str] = set()
    for r in results:
        all_keys |= set(r.only_in_a) | set(r.only_in_b) | set(r.mismatched)

    if not all_keys:
        return MomentumReport()

    # Build windows
    windows = [results[i: i + window] for i in range(0, len(results), window)]
    if len(windows) < 2:
        return MomentumReport()

    entries: List[MomentumEntry] = []
    for key in sorted(all_keys):
        counts = [sum(1 for r in w if _is_changed(key, r)) for w in windows]
        # acceleration = slope of counts over window indices
        n = len(counts)
        x_mean = (n - 1) / 2
        y_mean = sum(counts) / n
        num = sum((i - x_mean) * (counts[i] - y_mean) for i in range(n))
        den = sum((i - x_mean) ** 2 for i in range(n)) or 1.0
        accel = num / den
        entries.append(MomentumEntry(key=key, change_counts=counts, acceleration=accel))

    return MomentumReport(entries=entries)
