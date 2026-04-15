"""Tests for envdiff.cli_differ_profile."""
from __future__ import annotations

import json
import pathlib

import pytest
from click.testing import CliRunner

import click
from envdiff.cli_differ_profile import apply_profile_diff, profile_diff_options


@pytest.fixture()
def runner():
    return CliRunner()


def _write(path: pathlib.Path, content: str) -> None:
    path.write_text(content)


def _save_profile(profiles_dir: pathlib.Path, name: str, files: list[str]) -> None:
    profiles_dir.mkdir(parents=True, exist_ok=True)
    (profiles_dir / f"{name}.json").write_text(
        json.dumps({"name": name, "files": files})
    )


@click.command()
@profile_diff_options
def _dummy_cmd(profile_name, summary):
    has_diff = apply_profile_diff(profile_name, summary)
    raise SystemExit(1 if has_diff else 0)


def test_no_profile_flag_exits_zero(runner):
    result = runner.invoke(_dummy_cmd, [])
    assert result.exit_code == 0


def test_identical_profile_exits_zero(runner, tmp_path):
    env_a = tmp_path / ".env.a"
    env_b = tmp_path / ".env.b"
    _write(env_a, "KEY=same\n")
    _write(env_b, "KEY=same\n")
    profiles_dir = tmp_path / "profiles"
    _save_profile(profiles_dir, "myp", [str(env_a), str(env_b)])

    import envdiff.profiler as _p
    monkeypatch_dir = str(profiles_dir)

    import unittest.mock as mock
    with mock.patch("envdiff.differ_profile.get_profile",
                    side_effect=lambda name, **kw: json.loads(
                        (profiles_dir / f"{name}.json").read_text()
                    )):
        result = runner.invoke(_dummy_cmd, ["--profile", "myp"])
    assert result.exit_code == 0


def test_unknown_profile_exits_2(runner, tmp_path):
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()

    import unittest.mock as mock
    with mock.patch("envdiff.differ_profile.get_profile", return_value=None):
        result = runner.invoke(_dummy_cmd, ["--profile", "ghost"])
    assert result.exit_code == 2
