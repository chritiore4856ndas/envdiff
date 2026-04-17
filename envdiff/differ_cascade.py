"""Cascade diff: compare a chain of env files in order (e.g. base -> staging -> prod)."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from envdiff.comparator import compare, DiffResult


@dataclass
class CascadeStep:
    from_file: str
    to_file: str
    result: DiffResult

    def as_dict(self) -> dict:
        return {
            "from": self.from_file,
            "to": self.to_file,
            "only_in_a": sorted(self.result.only_in_a),
            "only_in_b": sorted(self.result.only_in_b),
            "mismatched": sorted(self.result.mismatched.keys()),
        }


@dataclass
class CascadeReport:
    steps: List[CascadeStep] = field(default_factory=list)

    def is_clean(self) -> bool:
        return all(
            not s.result.only_in_a and not s.result.only_in_b and not s.result.mismatched
            for s in self.steps
        )

    def all_drifting_keys(self) -> Dict[str, int]:
        """Return keys that differ in at least one step, with a count of how many steps."""
        counts: Dict[str, int] = {}
        for step in self.steps:
            for k in list(step.result.only_in_a) + list(step.result.only_in_b) + list(step.result.mismatched):
                counts[k] = counts.get(k, 0) + 1
        return dict(sorted(counts.items(), key=lambda x: -x[1]))

    def as_dict(self) -> dict:
        return {
            "clean": self.is_clean(),
            "steps": [s.as_dict() for s in self.steps],
            "drifting_keys": self.all_drifting_keys(),
        }


def cascade_diff(files: List[str]) -> CascadeReport:
    """Compare consecutive pairs in *files* and return a CascadeReport."""
    if len(files) < 2:
        raise ValueError("cascade_diff requires at least two files")

    from envdiff.parser import parse_env_file

    report = CascadeReport()
    for i in range(len(files) - 1):
        a, b = files[i], files[i + 1]
        env_a = parse_env_file(a)
        env_b = parse_env_file(b)
        result = compare(env_a, env_b)
        report.steps.append(CascadeStep(from_file=a, to_file=b, result=result))
    return report
