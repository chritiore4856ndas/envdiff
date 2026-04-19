import pytest
from envdiff.comparator import DiffResult
from envdiff.differ_variance import VarianceEntry, VarianceReport, variance_diff


def _result(matching=None, only_in_a=None, only_in_b=None, mismatched=None):
    return DiffResult(
        matching=matching or {},
        only_in_a=set(only_in_a or []),
        only_in_b=set(only_in_b or []),
        mismatched=mismatched or {},
    )


def test_empty_results_gives_empty_report():
    report = variance_diff([])
    assert report.entries == []


def test_single_result_matching_key_is_stable():
    r = _result(matching={"KEY": "val"})
    report = variance_diff([r])
    assert len(report.entries) == 1
    entry = report.entries[0]
    assert entry.key == "KEY"
    assert entry.is_stable is True
    assert entry.unique_count == 1


def test_mismatched_key_is_unstable():
    r = _result(mismatched={"KEY": ("a", "b")})
    report = variance_diff([r])
    entry = report.entries[0]
    assert entry.is_stable is False
    assert entry.unique_count == 2


def test_missing_key_is_unstable():
    r = _result(only_in_a={"MISSING"})
    report = variance_diff([r])
    entry = report.entries[0]
    assert entry.key == "MISSING"
    assert entry.is_stable is True  # only None values -> 1 unique


def test_multiple_results_stable_key():
    r1 = _result(matching={"K": "same"})
    r2 = _result(matching={"K": "same"})
    report = variance_diff([r1, r2])
    assert report.entries[0].is_stable is True


def test_multiple_results_unstable_key():
    r1 = _result(matching={"K": "v1"})
    r2 = _result(matching={"K": "v2"})
    report = variance_diff([r1, r2])
    assert report.entries[0].is_stable is False
    assert report.entries[0].unique_count == 2


def test_unstable_returns_only_unstable_entries():
    r1 = _result(matching={"STABLE": "x", "UNSTABLE": "a"})
    r2 = _result(matching={"STABLE": "x", "UNSTABLE": "b"})
    report = variance_diff([r1, r2])
    unstable = report.unstable()
    assert len(unstable) == 1
    assert unstable[0].key == "UNSTABLE"


def test_stable_returns_only_stable_entries():
    r1 = _result(matching={"STABLE": "x", "UNSTABLE": "a"})
    r2 = _result(matching={"STABLE": "x", "UNSTABLE": "b"})
    report = variance_diff([r1, r2])
    stable = report.stable()
    assert len(stable) == 1
    assert stable[0].key == "STABLE"


def test_as_dict_contains_entries():
    r = _result(matching={"K": "v"})
    report = variance_diff([r])
    d = report.as_dict()
    assert "entries" in d
    assert d["entries"][0]["key"] == "K"
