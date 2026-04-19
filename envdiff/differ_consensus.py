"""Consensus analysis: find keys whose values agree across a majority of results."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.comparator import DiffResult


@dataclass
class ConsensusEntry:
    key: str
    majority_value: Optional[str]
    agreement_count: int
    total: int
    dissenting_values: List[Optional[str]] = field(default_factory=list)

    @property
    def agreement_ratio(self) -> float:
        return self.agreement_count / self.total if self.total else 1.0

    @property
    def has_consensus(self) -> bool:
        return self.agreement_ratio > 0.5

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"ConsensusEntry(key={self.key!r}, "
            f"majority={self.majority_value!r}, "
            f"ratio={self.agreement_ratio:.2f})"
        )

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "majority_value": self.majority_value,
            "agreement_count": self.agreement_count,
            "total": self.total,
            "agreement_ratio": round(self.agreement_ratio, 4),
            "has_consensus": self.has_consensus,
            "dissenting_values": self.dissenting_values,
        }


@dataclass
class ConsensusReport:
    entries: List[ConsensusEntry] = field(default_factory=list)

    def contested(self) -> List[ConsensusEntry]:
        return [e for e in self.entries if not e.has_consensus]

    def agreed(self) -> List[ConsensusEntry]:
        return [e for e in self.entries if e.has_consensus]

    def as_dict(self) -> dict:
        return {
            "total_keys": len(self.entries),
            "agreed": len(self.agreed()),
            "contested": len(self.contested()),
            "entries": [e.as_dict() for e in self.entries],
        }


def consensus_results(results: List[DiffResult]) -> ConsensusReport:
    if not results:
        return ConsensusReport()

    all_keys: set = set()
    for r in results:
        all_keys |= set(r.only_in_a) | set(r.only_in_b) | set(r.mismatched) | set(r.matching)

    entries: List[ConsensusEntry] = []
    for key in sorted(all_keys):
        values: List[Optional[str]] = []
        for r in results:
            if key in r.matching:
                values.append(r.matching[key])
            elif key in r.mismatched:
                a_val, b_val = r.mismatched[key]
                values.extend([a_val, b_val])
            else:
                values.append(None)

        counter: Counter = Counter(values)
        majority_value, agreement_count = counter.most_common(1)[0]
        dissenting = [v for v in values if v != majority_value]

        entries.append(ConsensusEntry(
            key=key,
            majority_value=majority_value,
            agreement_count=agreement_count,
            total=len(values),
            dissenting_values=dissenting,
        ))

    return ConsensusReport(entries=entries)
