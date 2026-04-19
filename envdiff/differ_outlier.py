"""Detect outlier keys — keys whose values differ from the majority across multiple diff results."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Sequence

from envdiff.comparator import DiffResult


@dataclass
class OutlierEntry:
    key: str
    majority_value: str | None
    outlier_values: Dict[str, str | None]  # env_label -> value
    frequency: float  # fraction of envs where value matches majority

    def __repr__(self) -> str:
        return f"OutlierEntry({self.key!r}, majority={self.majority_value!r}, frequency={self.frequency:.2f})"

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "majority_value": self.majority_value,
            "outlier_values": self.outlier_values,
            "frequency": round(self.frequency, 4),
        }


@dataclass
class OutlierReport:
    entries: List[OutlierEntry] = field(default_factory=list)

    def outliers(self, threshold: float = 0.5) -> List[OutlierEntry]:
        """Return entries where majority frequency is below threshold."""
        return [e for e in self.entries if e.frequency < threshold]

    def as_dict(self) -> dict:
        return {"entries": [e.as_dict() for e in self.entries]}


def detect_outliers(
    results: Sequence[DiffResult],
    labels: Sequence[str] | None = None,
) -> OutlierReport:
    """Analyse value consistency for every key across multiple DiffResults."""
    if not results:
        return OutlierReport()

    if labels is None:
        labels = [str(i) for i in range(len(results))]

    # Collect all values per key across all envs (use merged view: a + b)
    key_values: Dict[str, Dict[str, str | None]] = {}
    for label, result in zip(labels, results):
        combined = {**result.only_in_a, **result.only_in_b, **result.mismatched_values}
        # also include matching
        for k, v in result.matching.items():
            combined.setdefault(k, v)
        for k, v in combined.items():
            key_values.setdefault(k, {})[label] = v

    entries: List[OutlierEntry] = []
    for key, env_vals in key_values.items():
        counter: Counter = Counter(env_vals.values())
        majority_value, majority_count = counter.most_common(1)[0]
        total = len(env_vals)
        frequency = majority_count / total
        outlier_envs = {lbl: val for lbl, val in env_vals.items() if val != majority_value}
        entries.append(
            OutlierEntry(
                key=key,
                majority_value=majority_value,
                outlier_values=outlier_envs,
                frequency=frequency,
            )
        )

    entries.sort(key=lambda e: e.frequency)
    return OutlierReport(entries=entries)
