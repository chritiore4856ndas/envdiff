"""Profile support: named environment profiles mapped to .env file paths."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

PROFILE_FILE = ".envdiff_profiles.json"


def _profile_path(directory: str = ".") -> Path:
    return Path(directory) / PROFILE_FILE


def save_profile(name: str, paths: List[str], directory: str = ".") -> None:
    """Register a named profile with a list of env file paths."""
    profile_file = _profile_path(directory)
    profiles: Dict[str, List[str]] = {}
    if profile_file.exists():
        profiles = json.loads(profile_file.read_text())
    profiles[name] = paths
    profile_file.write_text(json.dumps(profiles, indent=2))


def load_profiles(directory: str = ".") -> Dict[str, List[str]]:
    """Return all saved profiles, or empty dict if none exist."""
    profile_file = _profile_path(directory)
    if not profile_file.exists():
        return {}
    return json.loads(profile_file.read_text())


def get_profile(name: str, directory: str = ".") -> List[str]:
    """Return file paths for a named profile. Raises KeyError if not found."""
    profiles = load_profiles(directory)
    if name not in profiles:
        raise KeyError(f"Profile '{name}' not found. Available: {list(profiles.keys())}")
    return profiles[name]


def delete_profile(name: str, directory: str = ".") -> bool:
    """Remove a profile by name. Returns True if deleted, False if not found."""
    profile_file = _profile_path(directory)
    profiles = load_profiles(directory)
    if name not in profiles:
        return False
    del profiles[name]
    profile_file.write_text(json.dumps(profiles, indent=2))
    return True


def list_profiles(directory: str = ".") -> List[str]:
    """Return sorted list of profile names."""
    return sorted(load_profiles(directory).keys())
