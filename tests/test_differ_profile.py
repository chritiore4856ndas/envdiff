"""Tests for envdiff.differ_profile."""
from __future__ import annotations

import json
import os
import pathlib

import pytest

from envdiff.differ_profile import (
    ProfileDiffResult,
    ProfileNotFoundError,
    run_profile_diff,
)


@pytest.fixture()
def tmp_dir(tmp_path: pathlib.Path):
    return tmp_path


def _write(path: pathlib.Path, content: str) -> None:
    path.write_text(content)


def _save_profile(profiles_dir: pathlib.Path, name: str, files: list[str]) -> None:
    profiles_dir.mkdir(parents=True, exist_ok=True)
    profile_file = profiles_dir / f"{name}.json"
    profile_file.write_text(json.dumps({"name": name, "files": files}))


def test_run_profile_diff_returns_profile_diff_result(tmp_dir):
    env_a = tmp_dir / ".env.a"
    env_b = tmp_dir / ".env.b"
    _write(env_a, "KEY=value\n")
    _write(env_b, "KEY=value\n")

    profiles_dir = tmp_dir / "profiles"
    _save_profile(profiles_dir, "mypro", [str(env_a), str(env_b)])

    result = run_profile_diff("mypro", profiles_dir=str(profiles_dir))
    assert isinstance(result, ProfileDiffResult)
    assert result.profile_name == "mypro"
    assert not result.result.has_diff


def test_run_profile_diff_detects_mismatch(tmp_dir):
    env_a = tmp_dir / ".env.a"
    env_b = tmp_dir / ".env.b"
    _write(env_a, "KEY=foo\n")
    _write(env_b, "KEY=bar\n")

    profiles_dir = tmp_dir / "profiles"
    _save_profile(profiles_dir, "mypro", [str(env_a), str(env_b)])

    result = run_profile_diff("mypro", profiles_dir=str(profiles_dir))
    assert result.result.has_diff


def test_run_profile_diff_raises_when_profile_missing(tmp_dir):
    profiles_dir = tmp_dir / "profiles"
    profiles_dir.mkdir()
    with pytest.raises(ProfileNotFoundError):
        run_profile_diff("ghost", profiles_dir=str(profiles_dir))


def test_run_profile_diff_raises_when_no_files(tmp_dir):
    profiles_dir = tmp_dir / "profiles"
    _save_profile(profiles_dir, "empty", [])
    with pytest.raises(ValueError, match="no files"):
        run_profile_diff("empty", profiles_dir=str(profiles_dir))
