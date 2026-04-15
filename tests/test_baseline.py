"""Tests for envdiff.baseline."""
from __future__ import annotations

import json
import pytest

from envdiff.comparator import DiffResult
from envdiff.baseline import (
    save_baseline,
    load_baseline,
    diff_against_baseline,
    _DEFAULT_BASELINE,
)


@pytest.fixture()
def empty_result() -> DiffResult:
    return DiffResult(only_in_a={}, only_in_b={}, mismatched={})


@pytest.fixture()
def rich_result() -> DiffResult:
    return DiffResult(
        only_in_a={"ALPHA": "1"},
        only_in_b={"BETA": None},
        mismatched={"GAMMA": ("old", "new")},
    )


def test_save_creates_file(tmp_path, rich_result):
    dest = tmp_path / "baseline.json"
    returned = save_baseline(rich_result, str(dest))
    assert returned == dest
    assert dest.exists()


def test_save_content_is_valid_json(tmp_path, rich_result):
    dest = tmp_path / "baseline.json"
    save_baseline(rich_result, str(dest))
    data = json.loads(dest.read_text())
    assert data["only_in_a"] == {"ALPHA": "1"}
    assert data["only_in_b"] == {"BETA": None}
    assert data["mismatched"]["GAMMA"] == {"a": "old", "b": "new"}


def test_load_roundtrip(tmp_path, rich_result):
    dest = tmp_path / "baseline.json"
    save_baseline(rich_result, str(dest))
    loaded = load_baseline(str(dest))
    assert loaded.only_in_a == rich_result.only_in_a
    assert loaded.only_in_b == rich_result.only_in_b
    assert loaded.mismatched == rich_result.mismatched


def test_load_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError, match="Baseline file not found"):
        load_baseline(str(tmp_path / "nonexistent.json"))


def test_diff_against_baseline_removes_known_keys(rich_result):
    # current has the same issues plus one new one
    current = DiffResult(
        only_in_a={"ALPHA": "1", "NEW_KEY": "x"},
        only_in_b={"BETA": None},
        mismatched={"GAMMA": ("old", "new"), "DELTA": ("a", "b")},
    )
    delta = diff_against_baseline(current, rich_result)
    assert "ALPHA" not in delta.only_in_a
    assert "NEW_KEY" in delta.only_in_a
    assert "BETA" not in delta.only_in_b
    assert "GAMMA" not in delta.mismatched
    assert "DELTA" in delta.mismatched


def test_diff_against_empty_baseline_returns_full_result(empty_result, rich_result):
    delta = diff_against_baseline(rich_result, empty_result)
    assert delta.only_in_a == rich_result.only_in_a
    assert delta.only_in_b == rich_result.only_in_b
    assert delta.mismatched == rich_result.mismatched
