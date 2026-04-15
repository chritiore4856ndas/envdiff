"""Annotate a DiffResult with human-readable descriptions for each key."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from envdiff.comparator import DiffResult


@dataclass
class Annotation:
    key: str
    status: str  # 'missing_in_b', 'missing_in_a', 'mismatch', 'ok'
    note: str
    value_a: Optional[str] = None
    value_b: Optional[str] = None


@dataclass
class AnnotatedDiff:
    annotations: Dict[str, Annotation] = field(default_factory=dict)

    def all_keys(self) -> list[str]:
        return sorted(self.annotations.keys())

    def by_status(self, status: str) -> list[Annotation]:
        return [a for a in self.annotations.values() if a.status == status]


def annotate(result: DiffResult, descriptions: Optional[Dict[str, str]] = None) -> AnnotatedDiff:
    """Build an AnnotatedDiff from a DiffResult.

    Args:
        result: the comparison result to annotate.
        descriptions: optional mapping of key -> human description to embed in notes.
    """
    descs = descriptions or {}
    annotations: Dict[str, Annotation] = {}

    for key in result.only_in_a:
        desc = descs.get(key, "")
        note = f"Present in A but missing in B." + (f" {desc}" if desc else "")
        annotations[key] = Annotation(key=key, status="missing_in_b", note=note,
                                      value_a=result.values_a.get(key))

    for key in result.only_in_b:
        desc = descs.get(key, "")
        note = f"Present in B but missing in A." + (f" {desc}" if desc else "")
        annotations[key] = Annotation(key=key, status="missing_in_a", note=note,
                                      value_b=result.values_b.get(key))

    for key in result.mismatched:
        desc = descs.get(key, "")
        note = f"Values differ between A and B." + (f" {desc}" if desc else "")
        annotations[key] = Annotation(
            key=key,
            status="mismatch",
            note=note,
            value_a=result.values_a.get(key),
            value_b=result.values_b.get(key),
        )

    return AnnotatedDiff(annotations=annotations)
