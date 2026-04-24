"""Tests for envdiff.differ_churn."""
from __future__ import annotations

import pytest

from envdiff.comparator import DiffResult
from envdiff.differ_churn import ChurnEntry, ChurnReport, churn_diff


def _result(
    only_in_a=(),
    only_in_b=(),
    mismatched=None,
    matching=None,
) -> DiffResult:
    return DiffResult(
        only_in_a=set(only_in_a),
        only_in_b=set(only_in_b),
        mismatched=dict(mismatched or {}),
        matching=dict(matching or {}),
    )


def test_empty_results_gives_empty_report():
    report = churn_diff([])
    assert isinstance(report, ChurnReport)
    assert report.entries == []


def test_single_result_missing_key_counted():
    r = _result(only_in_a=["FOO"])
    report = churn_diff([r])
    keys = [e.key for e in report.entries]
    assert "FOO" in keys
    entry = next(e for e in report.entries if e.key == "FOO")
    assert entry.changes == 1
    assert entry.snapshots == 1
    assert entry.churn_rate == 1.0


def test_stable_key_has_zero_churn():
    r = _result(matching={"STABLE": ("val", "val")})
    report = churn_diff([r])
    entry = next(e for e in report.entries if e.key == "STABLE")
    assert entry.changes == 0
    assert entry.churn_rate == 0.0


def test_key_in_half_results_has_half_rate():
    r1 = _result(mismatched={"KEY": ("a", "b")})
    r2 = _result(matching={"KEY": ("b", "b")})
    report = churn_diff([r1, r2])
    entry = next(e for e in report.entries if e.key == "KEY")
    assert entry.changes == 1
    assert entry.snapshots == 2
    assert entry.churn_rate == pytest.approx(0.5)


def test_high_churn_filters_correctly():
    r1 = _result(mismatched={"A": ("x", "y")}, matching={"B": ("v", "v")})
    r2 = _result(mismatched={"A": ("y", "z")}, matching={"B": ("v", "v")})
    report = churn_diff([r1, r2])
    high = report.high_churn(threshold=0.5)
    high_keys = [e.key for e in high]
    assert "A" in high_keys
    assert "B" not in high_keys


def test_entries_sorted_by_churn_rate_descending():
    r1 = _result(mismatched={"FAST": ("a", "b")}, matching={"SLOW": ("v", "v")})
    r2 = _result(mismatched={"FAST": ("b", "c")}, matching={"SLOW": ("v", "v")})
    report = churn_diff([r1, r2])
    rates = [e.churn_rate for e in report.entries]
    assert rates == sorted(rates, reverse=True)


def test_as_dict_contains_expected_keys():
    r = _result(only_in_b=["NEW"])
    report = churn_diff([r])
    d = report.as_dict()
    assert "entries" in d
    assert all("churn_rate" in e for e in d["entries"])


def test_churn_rate_zero_when_no_snapshots():
    entry = ChurnEntry(key="X", changes=0, snapshots=0)
    assert entry.churn_rate == 0.0
