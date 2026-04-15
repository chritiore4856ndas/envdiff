"""Combine profiler + multi-diff: run a named profile's files through multi_diff."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from envdiff.differ import MultiDiffResult, multi_diff
from envdiff.profiler import get_profile


@dataclass
class ProfileDiffResult:
    profile_name: str
    files: List[str]
    result: MultiDiffResult


class ProfileNotFoundError(KeyError):
    """Raised when the requested profile does not exist."""


def run_profile_diff(profile_name: str, profiles_dir: str | None = None) -> ProfileDiffResult:
    """Load *profile_name* and run multi_diff over its file list.

    Parameters
    ----------
    profile_name:
        Name of the saved profile.
    profiles_dir:
        Optional override for the directory that stores profiles (passed
        straight through to :func:`get_profile`).

    Raises
    ------
    ProfileNotFoundError
        If no profile with *profile_name* exists.
    """
    kwargs = {}
    if profiles_dir is not None:
        kwargs["profiles_dir"] = profiles_dir

    profile = get_profile(profile_name, **kwargs)
    if profile is None:
        raise ProfileNotFoundError(f"Profile '{profile_name}' not found.")

    files: List[str] = profile.get("files", [])
    if not files:
        raise ValueError(f"Profile '{profile_name}' has no files defined.")

    result = multi_diff(files)
    return ProfileDiffResult(profile_name=profile_name, files=files, result=result)
