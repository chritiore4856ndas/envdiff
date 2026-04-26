"""Tests for envdiff.differ_maturity."""
import pytest

from envdiff.comparator import DiffResult
from envdiff.differ_maturity import MaturityEntry, MaturityReport, maturity_diff


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
    report = maturity_diff([])
    assert report.entries == []


def test_empty_results_average_rate_is_one():
    report = maturity_diff([])
    assert report.average_rate == 1.0


def test_single_result_matching_key_is_mature():
    r = _result(matching={"KEY": "val"})
    report = maturity_diff([r])
    assert len(report.entries) == 1
    entry = report.entries[0]
    assert entry.key == "KEY"
    assert entry.stable_count == 1
    assert entry.maturity_rate == 1.0
    assert entry.is_mature is True


def test_single_result_missing_key_has_zero_stability():
    r = _result(only_in_a={"GONE": "x"})
    report = maturity_diff([r])
    entry = report.entries[0]
    assert entry.stable_count == 0
    assert entry.maturity_rate == 0.0
    assert entry.is_mature is False


def test_key_stable_in_all_results_is_mature():
    results = [_result(matching={"K": str(i)}) for i in range(5)]
    report = maturity_diff(results)
    assert report.entries[0].maturity_rate == 1.0
    assert report.entries[0].is_mature is True


def test_key_stable_in_few_results_is_immature():
    stable = [_result(matching={"K": "v"}) for _ in range(1)]
    unstable = [_result(only_in_a={"K": "v"}) for _ in range(9)]
    report = maturity_diff(stable + unstable)
    entry = next(e for e in report.entries if e.key == "K")
    assert entry.maturity_rate == pytest.approx(0.1)
    assert entry.is_mature is False


def test_immature_filter_returns_only_immature_keys():
    r1 = _result(matching={"STABLE": "v"})
    r2 = _result(only_in_a={"FLAKY": "x"})
    report = maturity_diff([r1, r2])
    immature_keys = {e.key for e in report.immature()}
    assert "FLAKY" in immature_keys
    assert "STABLE" not in immature_keys


def test_mature_filter_returns_only_mature_keys():
    results = [_result(matching={"SOLID": "1", "WOBBLY": "v"}) for _ in range(10)]
    results[0] = _result(only_in_a={"WOBBLY": "v"}, matching={"SOLID": "1"})
    results[1] = _result(only_in_a={"WOBBLY": "v"}, matching={"SOLID": "1"})
    report = maturity_diff(results)
    mature_keys = {e.key for e in report.mature()}
    assert "SOLID" in mature_keys


def test_as_dict_contains_expected_keys():
    r = _result(matching={"X": "1"})
    report = maturity_diff([r])
    d = report.as_dict()
    assert "entries" in d
    assert "average_rate" in d
    assert d["entries"][0]["key"] == "X"


def test_average_rate_reflects_all_entries():
    r1 = _result(matching={"A": "1"})
    r2 = _result(only_in_a={"B": "2"})
    report = maturity_diff([r1, r2])
    # A: stable_count=1/1=1.0, B: stable_count=0/1=0.0 -> avg=0.5
    assert report.average_rate == pytest.approx(0.5)
