"""Tests for envdiff.differ (multi-file diff)."""
from __future__ import annotations

import pytest
from pathlib import Path

from envdiff.differ import multi_diff, MultiDiffResult


@pytest.fixture()
def tmp_envs(tmp_path: Path):
    def _write(name: str, content: str) -> str:
        p = tmp_path / name
        p.write_text(content)
        return str(p)
    return _write


def test_two_identical_files_no_differing_keys(tmp_envs):
    a = tmp_envs("a.env", "FOO=bar\nBAZ=qux\n")
    b = tmp_envs("b.env", "FOO=bar\nBAZ=qux\n")
    result = multi_diff(a, b)
    assert result.differing_keys == set()


def test_two_files_mismatch_detected(tmp_envs):
    a = tmp_envs("a.env", "FOO=bar\n")
    b = tmp_envs("b.env", "FOO=baz\n")
    result = multi_diff(a, b)
    assert "FOO" in result.differing_keys


def test_missing_key_in_one_file(tmp_envs):
    a = tmp_envs("a.env", "FOO=bar\nEXTRA=yes\n")
    b = tmp_envs("b.env", "FOO=bar\n")
    result = multi_diff(a, b)
    assert "EXTRA" in result.differing_keys


def test_three_files_matrix_has_all_keys(tmp_envs):
    a = tmp_envs("a.env", "A=1\n")
    b = tmp_envs("b.env", "B=2\n")
    c = tmp_envs("c.env", "C=3\n")
    result = multi_diff(a, b, c)
    assert set(result.matrix.keys()) == {"A", "B", "C"}


def test_pairwise_keys_correct(tmp_envs):
    a = tmp_envs("a.env", "X=1\n")
    b = tmp_envs("b.env", "X=1\n")
    c = tmp_envs("c.env", "X=2\n")
    result = multi_diff(a, b, c)
    pairs = list(result.pairwise.keys())
    assert len(pairs) == 3  # (a,b), (a,c), (b,c)


def test_files_list_preserved_in_order(tmp_envs):
    a = tmp_envs("a.env", "K=v\n")
    b = tmp_envs("b.env", "K=v\n")
    c = tmp_envs("c.env", "K=v\n")
    result = multi_diff(a, b, c)
    assert result.files == [a, b, c]


def test_none_value_in_matrix_for_missing_key(tmp_envs):
    a = tmp_envs("a.env", "ONLY_A=1\n")
    b = tmp_envs("b.env", "")
    result = multi_diff(a, b)
    assert result.matrix["ONLY_A"][b] is None
