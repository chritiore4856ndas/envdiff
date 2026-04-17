"""Generate a patch (suggested additions) to reconcile two env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.comparator import DiffResult


@dataclass
class PatchLine:
    key: str
    value: Optional[str]
    reason: str  # 'missing_in_b' | 'missing_in_a' | 'mismatch'

    def as_env_line(self) -> str:
        if self.value is None:
            return f"{self.key}="
        return f"{self.key}={self.value}"

    def as_dict(self) -> dict:
        return {"key": self.key, "value": self.value, "reason": self.reason}


@dataclass
class PatchReport:
    lines: List[PatchLine] = field(default_factory=list)

    def is_empty(self) -> bool:
        return len(self.lines) == 0

    def for_reason(self, reason: str) -> List[PatchLine]:
        return [l for l in self.lines if l.reason == reason]

    def as_dict(self) -> dict:
        return {"patch": [l.as_dict() for l in self.lines]}

    def as_env_lines(self) -> List[str]:
        return [l.as_env_line() for l in self.lines]


def build_patch(result: DiffResult, target: str = "b") -> PatchReport:
    """Build a patch that brings *target* env in sync with the other.

    target='b'  -> lines to add/fix in file B so it matches A
    target='a'  -> lines to add/fix in file A so it matches B
    """
    lines: List[PatchLine] = []

    if target == "b":
        for key, val in sorted(result.only_in_a.items()):
            lines.append(PatchLine(key=key, value=val, reason="missing_in_b"))
        for key, (val_a, _val_b) in sorted(result.mismatched.items()):
            lines.append(PatchLine(key=key, value=val_a, reason="mismatch"))
    else:
        for key, val in sorted(result.only_in_b.items()):
            lines.append(PatchLine(key=key, value=val, reason="missing_in_a"))
        for key, (_val_a, val_b) in sorted(result.mismatched.items()):
            lines.append(PatchLine(key=key, value=val_b, reason="mismatch"))

    return PatchReport(lines=lines)
