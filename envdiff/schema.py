"""Schema validation for .env files.

Allows users to define required keys (and optional expected types/patterns)
so envdiff can warn when a key is missing or its value looks wrong.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class SchemaRule:
    key: str
    required: bool = True
    pattern: Optional[str] = None  # regex the value must match
    description: str = ""


@dataclass
class SchemaViolation:
    key: str
    reason: str  # "missing" | "pattern_mismatch"
    expected_pattern: Optional[str] = None
    actual_value: Optional[str] = None


@dataclass
class SchemaResult:
    violations: List[SchemaViolation] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.violations) == 0


def load_schema(path: str | Path) -> List[SchemaRule]:
    """Load a JSON schema file and return a list of SchemaRules."""
    data = json.loads(Path(path).read_text())
    rules = []
    for entry in data.get("keys", []):
        rules.append(
            SchemaRule(
                key=entry["key"],
                required=entry.get("required", True),
                pattern=entry.get("pattern"),
                description=entry.get("description", ""),
            )
        )
    return rules


def validate(env: Dict[str, Optional[str]], rules: List[SchemaRule]) -> SchemaResult:
    """Validate an env dict against a list of SchemaRules."""
    result = SchemaResult()
    for rule in rules:
        if rule.key not in env or env[rule.key] is None:
            if rule.required:
                result.violations.append(
                    SchemaViolation(key=rule.key, reason="missing")
                )
            continue
        value = env[rule.key]
        if rule.pattern and not re.fullmatch(rule.pattern, value or ""):
            result.violations.append(
                SchemaViolation(
                    key=rule.key,
                    reason="pattern_mismatch",
                    expected_pattern=rule.pattern,
                    actual_value=value,
                )
            )
    return result
