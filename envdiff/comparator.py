"""Compare two parsed .env dicts and produce a structured diff result."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DiffResult:
    """Holds the comparison results between two env files."""

    only_in_a: List[str] = field(default_factory=list)   # keys missing from b
    only_in_b: List[str] = field(default_factory=list)   # keys missing from a
    mismatched: Dict[str, tuple] = field(default_factory=dict)  # key -> (val_a, val_b)
    matching: List[str] = field(default_factory=list)    # identical keys+values

    @property
    def has_diff(self) -> bool:
        return bool(self.only_in_a or self.only_in_b or self.mismatched)


def compare(
    env_a: Dict[str, Optional[str]],
    env_b: Dict[str, Optional[str]],
) -> DiffResult:
    """
    Compare two env dicts.

    Args:
        env_a: parsed env from the first file (e.g. .env)
        env_b: parsed env from the second file (e.g. .env.production)

    Returns:
        DiffResult with categorised keys.
    """
    result = DiffResult()
    all_keys = set(env_a) | set(env_b)

    for key in sorted(all_keys):
        in_a = key in env_a
        in_b = key in env_b

        if in_a and not in_b:
            result.only_in_a.append(key)
        elif in_b and not in_a:
            result.only_in_b.append(key)
        elif env_a[key] != env_b[key]:
            result.mismatched[key] = (env_a[key], env_b[key])
        else:
            result.matching.append(key)

    return result
