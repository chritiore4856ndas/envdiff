"""Lint .env files for common style and correctness issues."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class LintIssue:
    line_number: int
    key: str | None
    message: str
    severity: str  # "warning" | "error"


@dataclass
class LintResult:
    path: str
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.issues) == 0

    @property
    def errors(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "warning"]


def lint_env_file(path: str | Path) -> LintResult:
    """Lint a single .env file and return a LintResult."""
    path = Path(path)
    result = LintResult(path=str(path))

    if not path.exists():
        result.issues.append(LintIssue(0, None, f"File not found: {path}", "error"))
        return result

    seen_keys: dict[str, int] = {}

    for lineno, raw in enumerate(path.read_text().splitlines(), start=1):
        line = raw.strip()

        if not line or line.startswith("#"):
            continue

        if "=" not in line:
            result.issues.append(
                LintIssue(lineno, None, f"Line missing '=': {raw!r}", "error")
            )
            continue

        key, _, value = line.partition("=")
        key = key.strip()

        if not key:
            result.issues.append(
                LintIssue(lineno, key, "Empty key name", "error")
            )
            continue

        if key != key.upper():
            result.issues.append(
                LintIssue(lineno, key, f"Key '{key}' is not uppercase", "warning")
            )

        if " " in key:
            result.issues.append(
                LintIssue(lineno, key, f"Key '{key}' contains spaces", "error")
            )

        if key in seen_keys:
            result.issues.append(
                LintIssue(
                    lineno,
                    key,
                    f"Duplicate key '{key}' (first seen on line {seen_keys[key]})",
                    "warning",
                )
            )
        else:
            seen_keys[key] = lineno

        if not value.strip():
            result.issues.append(
                LintIssue(lineno, key, f"Key '{key}' has no value", "warning")
            )

    return result
