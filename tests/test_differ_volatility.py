"""Tests for envdiff.differ_volatility."""
import pytest

from envdiff.comparator import DiffResult
from envdiff.differ_volatility import VolatilityEntry, VolatilityReport, volatility_diff


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
    report = volatility_diff([])
    assert report.entries == []
    assert report.volatile() == []
    assert report.stable() == []


def test_single_result_matching_key_has_zero_changes():
    r = _result(matching={"KEY": "val"})
    report = volatility_diff([r])
    assert len(report.entries) == 1
    entry = report.entries[0]
    assert entry.key == "KEY"
    assert entry.change_count == 0
    assert entry.snapshot_count == 1
    assert entry.volatility_rate == 0.0
    assert not entry.is_volatile


def test_single_result_missing_key_has_one_change():
    r = _result(only_in_a={"MISSING": "x"})
    report = volatility_diff([r])
    entry = report.entries[0]
    assert entry.key == "MISSING"
    assert entry.change_count == 1
    assert entry.snapshot_count == 1
    assert entry.volatility_rate == 1.0
    assert entry.is_volatile


def test_key_changing_in_all_results_is_fully_volatile():
    results = [
        _result(mismatched={"FLAKY": ("a", "b")}),
        _result(mismatched={"FLAKY": ("b", "c")}),
        _result(mismatched={"FLAKY": ("c", "d")}),
    ]
    report = volatility_diff(results)
    entry = next(e for e in report.entries if e.key == "FLAKY")
    assert entry.change_count == 3
    assert entry.volatility_rate == 1.0
    assert entry.is_volatile


def test_key_stable_across_all_results_has_zero_rate():
    results = [
        _result(matching={"STABLE": "v"}),
        _result(matching={"STABLE": "v"}),
        _result(matching={"STABLE": "v"}),
    ]
    report = volatility_diff(results)
    entry = report.entries[0]
    assert entry.key == "STABLE"
    assert entry.change_count == 0
    assert entry.volatility_rate == 0.0
    assert not entry.is_volatile


def test_volatile_and_stable_split_correctly():
    results = [
        _result(matching={"STABLE": "v"}, mismatched={"FLAKY": ("a", "b")}),
        _result(matching={"STABLE": "v"}, mismatched={"FLAKY": ("b", "c")}),
    ]
    report = volatility_diff(results)
    assert len(report.volatile()) == 1
    assert report.volatile()[0].key == "FLAKY"
    assert len(report.stable()) == 1
    assert report.stable()[0].key == "STABLE"


def test_as_dict_contains_expected_keys():
    r = _result(matching={"A": "1"}, only_in_a={"B": "2"})
    report = volatility_diff([r])
    d = report.as_dict()
    assert "entries" in d
    assert "volatile_count" in d
    assert "stable_count" in d
    assert d["volatile_count"] + d["stable_count"] == len(report.entries)


def test_entry_as_dict_shape():
    entry = VolatilityEntry(key="X", change_count=2, snapshot_count=4)
    d = entry.as_dict()
    assert d["key"] == "X"
    assert d["change_count"] == 2
    assert d["snapshot_count"] == 4
    assert d["volatility_rate"] == 0.5
    assert not d["is_volatile"]
