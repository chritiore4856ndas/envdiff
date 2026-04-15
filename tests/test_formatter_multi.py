"""Tests for envdiff.formatter_multi."""
from __future__ import annotations

import pytest
from pathlib import Path

from envdiff.differ import multi_diff
from envdiff.formatter_multi import format_multi_text, format_multi_summary


@pytest.fixture()
def tmp_envs(tmp_path: Path):
    def _write(name: str, content: str) -> str:
        p = tmp_path / name
        p.write_text(content)
        return str(p)
    return _write


def test_identical_files_returns_identical_message(tmp_envs):
    a = tmp_envs("a.env", "FOO=bar\n")
    b = tmp_envs("b.env", "FOO=bar\n")
    result = multi_diff(a, b)
    out = format_multi_text(result)
    assert "identical" in out.lower() or out.strip() == "All files are identical."


def test_differing_key_appears_in_output(tmp_envs):
    a = tmp_envs("a.env", "FOO=bar\n")
    b = tmp_envs("b.env", "FOO=baz\n")
    result = multi_diff(a, b)
    out = format_multi_text(result)
    assert "FOO" in out


def test_missing_key_shows_missing_label(tmp_envs):
    a = tmp_envs("a.env", "EXTRA=yes\n")
    b = tmp_envs("b.env", "")
    result = multi_diff(a, b)
    out = format_multi_text(result)
    assert "missing" in out.lower()


def test_summary_shows_difference_count(tmp_envs):
    a = tmp_envs("a.env", "X=1\nY=2\n")
    b = tmp_envs("b.env", "X=9\n")
    result = multi_diff(a, b)
    out = format_multi_summary(result)
    assert "difference" in out.lower()


def test_summary_identical_pair(tmp_envs):
    a = tmp_envs("a.env", "K=v\n")
    b = tmp_envs("b.env", "K=v\n")
    result = multi_diff(a, b)
    out = format_multi_summary(result)
    assert "identical" in out.lower()


def test_header_contains_filenames(tmp_envs):
    a = tmp_envs("prod.env", "A=1\nB=2\n")
    b = tmp_envs("staging.env", "A=1\nB=9\n")
    result = multi_diff(a, b)
    out = format_multi_text(result)
    assert "prod.env" in out
    assert "staging.env" in out
