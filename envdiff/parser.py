"""Parser for .env files."""

import re
from pathlib import Path
from typing import Dict, Optional


COMMENT_RE = re.compile(r"^\s*#.*$")
BLANK_RE = re.compile(r"^\s*$")
KEY_VALUE_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$")


def parse_env_file(path: str | Path) -> Dict[str, Optional[str]]:
    """
    Parse a .env file and return a dict of key -> value.

    - Ignores blank lines and comment lines (starting with #)
    - Strips surrounding quotes from values
    - Returns None as value for keys declared without a value (KEY=)
    """
    env: Dict[str, Optional[str]] = {}
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"env file not found: {file_path}")

    with file_path.open(encoding="utf-8") as f:
        for lineno, raw_line in enumerate(f, start=1):
            line = raw_line.rstrip("\n")

            if BLANK_RE.match(line) or COMMENT_RE.match(line):
                continue

            match = KEY_VALUE_RE.match(line)
            if not match:
                raise ValueError(
                    f"Invalid syntax at {file_path}:{lineno} -> {line!r}"
                )

            key, value = match.group(1), match.group(2).strip()
            value = _strip_quotes(value) if value else None
            env[key] = value

    return env


def _strip_quotes(value: str) -> str:
    """Remove surrounding single or double quotes from a value."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        return value[1:-1]
    return value
