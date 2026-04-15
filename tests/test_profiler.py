"""Tests for envdiff.profiler."""
from __future__ import annotations

import json
import pytest

from envdiff.profiler import (
    save_profile,
    load_profiles,
    get_profile,
    delete_profile,
    list_profiles,
    PROFILE_FILE,
)


@pytest.fixture()
def tmp_dir(tmp_path):
    return str(tmp_path)


def test_save_creates_profile_file(tmp_dir):
    save_profile("dev", [".env.dev"], directory=tmp_dir)
    import os
    assert os.path.exists(os.path.join(tmp_dir, PROFILE_FILE))


def test_save_content_is_valid_json(tmp_dir):
    save_profile("dev", [".env.dev", ".env.local"], directory=tmp_dir)
    from pathlib import Path
    data = json.loads((Path(tmp_dir) / PROFILE_FILE).read_text())
    assert data["dev"] == [".env.dev", ".env.local"]


def test_load_profiles_empty_when_no_file(tmp_dir):
    result = load_profiles(directory=tmp_dir)
    assert result == {}


def test_load_profiles_roundtrip(tmp_dir):
    save_profile("staging", [".env.staging"], directory=tmp_dir)
    profiles = load_profiles(directory=tmp_dir)
    assert "staging" in profiles
    assert profiles["staging"] == [".env.staging"]


def test_get_profile_returns_paths(tmp_dir):
    save_profile("prod", [".env.prod"], directory=tmp_dir)
    paths = get_profile("prod", directory=tmp_dir)
    assert paths == [".env.prod"]


def test_get_profile_raises_on_missing(tmp_dir):
    with pytest.raises(KeyError, match="nope"):
        get_profile("nope", directory=tmp_dir)


def test_multiple_profiles_coexist(tmp_dir):
    save_profile("dev", [".env.dev"], directory=tmp_dir)
    save_profile("prod", [".env.prod"], directory=tmp_dir)
    profiles = load_profiles(directory=tmp_dir)
    assert set(profiles.keys()) == {"dev", "prod"}


def test_delete_profile_removes_entry(tmp_dir):
    save_profile("dev", [".env.dev"], directory=tmp_dir)
    deleted = delete_profile("dev", directory=tmp_dir)
    assert deleted is True
    assert "dev" not in load_profiles(directory=tmp_dir)


def test_delete_profile_returns_false_when_missing(tmp_dir):
    result = delete_profile("ghost", directory=tmp_dir)
    assert result is False


def test_list_profiles_sorted(tmp_dir):
    save_profile("zeta", [], directory=tmp_dir)
    save_profile("alpha", [], directory=tmp_dir)
    save_profile("beta", [], directory=tmp_dir)
    assert list_profiles(directory=tmp_dir) == ["alpha", "beta", "zeta"]


def test_list_profiles_empty_when_no_file(tmp_dir):
    assert list_profiles(directory=tmp_dir) == []
