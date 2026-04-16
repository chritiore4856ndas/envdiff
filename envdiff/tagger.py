"""Tag keys in a DiffResult with arbitrary labels for grouping or reporting."""

from __future__ import annotations

from dataclasses import dataclass, field
from fnmatch import fnmatch
from typing import Dict, List, Set

from envdiff.comparator import DiffResult


@dataclass
class TaggedDiff:
    """A DiffResult where every key carries a set of string tags."""

    result: DiffResult
    tags: Dict[str, Set[str]] = field(default_factory=dict)

    def keys_for_tag(self, tag: str) -> List[str]:
        """Return all keys that carry *tag*."""
        return [k for k, ts in self.tags.items() if tag in ts]

    def tags_for_key(self, key: str) -> Set[str]:
        """Return the set of tags assigned to *key* (empty set if none)."""
        return self.tags.get(key, set())


def tag_diff(
    result: DiffResult,
    rules: Dict[str, List[str]],
) -> TaggedDiff:
    """Assign tags to every key in *result* according to glob *rules*.

    Args:
        result: the DiffResult whose keys will be tagged.
        rules: mapping of ``tag -> [glob_pattern, ...]``.  A key receives a
               tag when it matches **any** of that tag's patterns.

    Returns:
        A :class:`TaggedDiff` with tags populated for every key that appears
        in *result* (missing_in_b, missing_in_a, or mismatched).
    """
    all_keys: Set[str] = (
        set(result.missing_in_b)
        | set(result.missing_in_a)
        | set(result.mismatched)
    )

    tags: Dict[str, Set[str]] = {k: set() for k in all_keys}

    for tag, patterns in rules.items():
        for key in all_keys:
            if any(fnmatch(key, pat) for pat in patterns):
                tags[key].add(tag)

    return TaggedDiff(result=result, tags=tags)
