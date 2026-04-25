"""Tests for envdiff.differ_gravity."""
from __future__ import annotations

import pytest

from envdiff.comparator import DiffResult
from envdiff.differ_gravity import GravityEntry, GravityReport, gravity_diff


def _result(
    matching=None,
    only_in_a=None,
    only_in_b=None,
    mismatched=None,
) -> DiffResult:
    return DiffResult(
        matching=matching or {},
        only_in_a=only_in_a or {},
        only_in_b=only_in_b or {},
        mismatched=mismatched or {},
    )


def test_empty_results_gives_empty_report():
    report = gravity_diff([])
    assert report.entries == []


def test_single_result_matching_key_has_zero_issues():
    r = _result(matching={"KEY": "val"})
    report = gravity_diff([r])
    assert len(report.entries) == 1
    entry = report.entries[0]
    assert entry.key == "KEY"
    assert entry.issues == 0
    assert entry.gravity_score == 0.0


def test_single_result_missing_key_has_score_one():
    r = _result(only_in_a={"KEY": "val"})
    report = gravity_diff([r])
    entry = next(e for e in report.entries if e.key == "KEY")
    assert entry.gravity_score == 1.0
    assert entry.is_heavy


def test_mismatched_key_counted_as_issue():
    r = _result(mismatched={"KEY": ("a", "b")})
    report = gravity_diff([r])
    entry = next(e for e in report.entries if e.key == "KEY")
    assert entry.issues == 1
    assert entry.gravity_score == 1.0


def test_key_in_half_results_has_half_score():
    r1 = _result(only_in_a={"KEY": "v"})
    r2 = _result(matching={"KEY": "v"})
    report = gravity_diff([r1, r2])
    entry = next(e for e in report.entries if e.key == "KEY")
    assert entry.gravity_score == pytest.approx(0.5)
    assert not entry.is_heavy  # exactly 0.5 is heavy


def test_is_heavy_at_exactly_half():
    r1 = _result(only_in_a={"KEY": "v"})
    r2 = _result(matching={"KEY": "v"})
    report = gravity_diff([r1, r2])
    entry = next(e for e in report.entries if e.key == "KEY")
    # 0.5 >= 0.5 → heavy
    assert entry.is_heavy


def test_entries_sorted_descending_by_score():
    r = _result(only_in_a={"A": "1"}, matching={"B": "2"})
    report = gravity_diff([r])
    scores = [e.gravity_score for e in report.entries]
    assert scores == sorted(scores, reverse=True)


def test_top_returns_n_entries():
    results = [
        _result(only_in_a={"X": "1", "Y": "2", "Z": "3"}),
    ]
    report = gravity_diff(results)
    assert len(report.top(2)) == 2


def test_heavy_filters_correctly():
    r1 = _result(only_in_a={"BAD": "x"})
    r2 = _result(matching={"GOOD": "y"})
    report = gravity_diff([r1, r2])
    heavy_keys = {e.key for e in report.heavy()}
    assert "BAD" in heavy_keys
    assert "GOOD" not in heavy_keys


def test_as_dict_contains_entries():
    r = _result(only_in_a={"K": "v"})
    report = gravity_diff([r])
    d = report.as_dict()
    assert "entries" in d
    assert d["entries"][0]["key"] == "K"
