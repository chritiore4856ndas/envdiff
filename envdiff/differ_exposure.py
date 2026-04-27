"""Exposure analysis: how often each key is 'exposed' (present and differing) across snapshots."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from envdiff.comparator import DiffResult


@dataclass
class ExposureEntry:
    key: str
    appearances: int
    exposures: int  # times the key was missing or mismatched

    @property
    def exposure_rate(self) -> float:
        if self.appearances == 0:
            return 0.0
        return self.exposures / self.appearances

    @property
    def is_exposed(self, threshold: float = 0.5) -> bool:
        return self.exposure_rate >= threshold

    def __repr__(self) -> str:
        return f"ExposureEntry(key={self.key!r}, rate={self.exposure_rate:.2f})"

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "appearances": self.appearances,
            "exposures": self.exposures,
            "exposure_rate": round(self.exposure_rate, 4),
        }


@dataclass
class ExposureReport:
    entries: List[ExposureEntry] = field(default_factory=list)

    def most_exposed(self) -> Optional[ExposureEntry]:
        if not self.entries:
            return None
        return max(self.entries, key=lambda e: e.exposure_rate)

    def exposed(self, threshold: float = 0.5) -> List[ExposureEntry]:
        return [e for e in self.entries if e.exposure_rate >= threshold]

    def as_dict(self) -> dict:
        return {"entries": [e.as_dict() for e in self.entries]}


def exposure_diff(results: List[DiffResult]) -> ExposureReport:
    if not results:
        return ExposureReport()

    all_keys: set = set()
    for r in results:
        all_keys |= set(r.only_in_a) | set(r.only_in_b) | set(r.mismatched) | set(r.matching)

    entries: List[ExposureEntry] = []
    for key in sorted(all_keys):
        appearances = 0
        exposures = 0
        for r in results:
            present = key in r.only_in_a or key in r.only_in_b or key in r.mismatched or key in r.matching
            if present:
                appearances += 1
            if key in r.only_in_a or key in r.only_in_b or key in r.mismatched:
                exposures += 1
        entries.append(ExposureEntry(key=key, appearances=appearances, exposures=exposures))

    return ExposureReport(entries=entries)
